from __future__ import annotations

from datetime import datetime, timezone

from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .core.config import get_settings
from .core.logging import configure_logging, get_logger
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

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await _init_db()
        logger.info("app.startup")
        yield

    app.router.lifespan_context = lifespan

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
    async def health() -> HealthStatus:
        return HealthStatus(
            environment=settings.environment,
            timestamp=datetime.now(timezone.utc),
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
        doc = await db.get(Document, document_id)
        if not doc or doc.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return DocumentRead(
            id=doc.id,
            title=doc.title,
            text=doc.text,
            created_at=doc.created_at,
        )

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
    return app


app = create_app()

