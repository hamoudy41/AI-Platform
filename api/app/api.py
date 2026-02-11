from __future__ import annotations

from datetime import datetime, timezone

import orjson
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .core.config import get_settings
from .core.logging import configure_logging, get_logger
from .core.metrics import REQUEST_COUNT, REQUEST_LATENCY, get_metrics, metrics_content_type
from .core.redis import cache_key, check_rate_limit, close_redis, get_cached, set_cached
from .db import get_db_session, get_engine
from .models import Base, Document
from .schemas import (
    AskRequest,
    AskResponse,
    ClassifyRequest,
    ClassifyResponse,
    DocumentCreate,
    DocumentRead,
    HealthStatus,
    NotarySummarizeRequest,
    NotarySummarizeResponse,
)
from .services_ai_flows import (
    AiFlowError,
    run_ask_flow,
    run_classify_flow,
    run_notary_summarization_flow,
)
from .services_llm import llm_client


logger = get_logger(__name__)


async def _init_db() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def create_app() -> FastAPI:
    configure_logging()

    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        default_response_class=ORJSONResponse,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await _init_db()
        logger.info("app.startup")
        yield
        await close_redis()
        logger.info("app.shutdown")

    app.router.lifespan_context = lifespan

    if settings.enable_prometheus:

        @app.middleware("http")
        async def metrics_middleware(request: Request, call_next):
            import time

            start = time.perf_counter()
            response = await call_next(request)
            elapsed = time.perf_counter() - start
            path = request.scope.get("path", "")
            method = request.method
            REQUEST_LATENCY.labels(method=method, path=path).observe(elapsed)
            REQUEST_COUNT.labels(method=method, path=path, status=response.status_code).inc()
            return response

    if settings.redis_url and settings.api_v1_prefix:

        @app.middleware("http")
        async def rate_limit_middleware(request: Request, call_next):
            if not request.url.path.startswith(f"{settings.api_v1_prefix}/"):
                return await call_next(request)
            tenant_id = request.headers.get(settings.tenant_header_name) or settings.default_tenant_id
            limit = getattr(settings, "rate_limit_per_minute", 120)
            if not await check_rate_limit(tenant_id, limit=limit, window_seconds=60):
                return ORJSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded. Try again later."},
                )
            return await call_next(request)

    if settings.api_key:
        _no_auth_paths = {"/metrics", f"{settings.api_v1_prefix}/health"}

        @app.middleware("http")
        async def api_key_middleware(request: Request, call_next):
            if request.url.path in _no_auth_paths:
                return await call_next(request)
            if request.url.path.startswith(f"{settings.api_v1_prefix}/"):
                key = request.headers.get("X-API-Key")
                if key != settings.api_key:
                    return ORJSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid or missing API key"},
                    )
            return await call_next(request)

    if settings.enable_prometheus:

        @app.get("/metrics", include_in_schema=False)
        async def metrics() -> Response:
            return Response(content=get_metrics(), media_type=metrics_content_type())

    @app.exception_handler(AiFlowError)
    async def ai_flow_error_handler(_: Request, exc: AiFlowError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc), "error_type": "ai_flow_error"},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> ORJSONResponse:
        logger.error("app.unhandled_error", error=str(exc))
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error_type": "internal_error"},
        )

    api_router = APIRouter(prefix=settings.api_v1_prefix)

    async def get_tenant_id(
        x_tenant_id: str | None = Header(default=None, alias=settings.tenant_header_name),
    ) -> str:
        return x_tenant_id or settings.default_tenant_id

    @api_router.get("/health", response_model=HealthStatus)
    async def health(db: AsyncSession = Depends(get_db_session)) -> HealthStatus:
        db_ok: bool | None = None
        try:
            await db.execute(text("SELECT 1"))
            db_ok = True
        except Exception as exc:  # noqa: BLE001
            logger.warning("health.db_check_failed", error=str(exc))
            db_ok = False
        llm_ok = llm_client.is_configured()
        return HealthStatus(
            environment=settings.environment,
            timestamp=datetime.now(timezone.utc),
            db_ok=db_ok,
            llm_ok=llm_ok,
        )

    @api_router.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
    async def create_document(
        payload: DocumentCreate,
        tenant_id: str = Depends(get_tenant_id),
        db: AsyncSession = Depends(get_db_session),
    ) -> DocumentRead:
        doc = Document(
            id=payload.id,
            tenant_id=tenant_id,
            title=payload.title,
            text=payload.text,
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return DocumentRead(
            id=doc.id,
            title=doc.title,
            text=doc.text,
            created_at=doc.created_at,
        )

    @api_router.get("/documents/{document_id}", response_model=DocumentRead)
    async def get_document(
        document_id: str,
        tenant_id: str = Depends(get_tenant_id),
        db: AsyncSession = Depends(get_db_session),
    ) -> DocumentRead:
        ck = cache_key(tenant_id, "document", document_id)
        cached = await get_cached(ck)
        if cached:
            return DocumentRead.model_validate(orjson.loads(cached))
        doc = await db.get(Document, document_id)
        if not doc or doc.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        out = DocumentRead(
            id=doc.id,
            title=doc.title,
            text=doc.text,
            created_at=doc.created_at,
        )
        await set_cached(ck, orjson.dumps(out.model_dump(mode="json")).decode(), ttl_seconds=300)
        return out

    @api_router.post(
        "/ai/notary/summarize",
        response_model=NotarySummarizeResponse,
        status_code=status.HTTP_200_OK,
    )
    async def notary_summarize(
        payload: NotarySummarizeRequest,
        tenant_id: str = Depends(get_tenant_id),
        db: AsyncSession = Depends(get_db_session),
    ) -> NotarySummarizeResponse:
        return await run_notary_summarization_flow(
            tenant_id=tenant_id,
            db=db,
            payload=payload,
        )

    @api_router.post(
        "/ai/classify",
        response_model=ClassifyResponse,
        status_code=status.HTTP_200_OK,
    )
    async def classify(
        payload: ClassifyRequest,
        tenant_id: str = Depends(get_tenant_id),
        db: AsyncSession = Depends(get_db_session),
    ) -> ClassifyResponse:
        return await run_classify_flow(tenant_id=tenant_id, db=db, payload=payload)

    @api_router.post(
        "/ai/ask",
        response_model=AskResponse,
        status_code=status.HTTP_200_OK,
    )
    async def ask(
        payload: AskRequest,
        tenant_id: str = Depends(get_tenant_id),
        db: AsyncSession = Depends(get_db_session),
    ) -> AskResponse:
        return await run_ask_flow(tenant_id=tenant_id, db=db, payload=payload)

    app.include_router(api_router)

    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="frontend")

    return app


app = create_app()
