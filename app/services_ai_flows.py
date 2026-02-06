from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .core.logging import get_logger
from .models import AiCallAudit, Document
from .schemas import NotarySummarizeRequest, NotarySummarizeResponse, NotarySummary
from .services_llm import LLMError, llm_client


logger = get_logger(__name__)


class AiFlowError(Exception):
    pass


async def run_notary_summarization_flow(
    *,
    tenant_id: str,
    db: AsyncSession,
    payload: NotarySummarizeRequest,
) -> NotarySummarizeResponse:
    text = payload.text
    if payload.document_id:
        stmt = select(Document).where(
            Document.id == payload.document_id,
            Document.tenant_id == tenant_id,
        )
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()
        if document:
            text = document.text

    prompt = (
        "You are an assistant for Dutch notarial offices. "
        "Summarize the following document in a structured, neutral way. "
        "Only summarize; do not give legal advice or speculate. "
        "Output MUST contain: title; bullet points of key points; parties involved; "
        "any explicit risks or warnings mentioned.\n\n"
        f"LANGUAGE: {payload.language.upper()}\n"
        "DOCUMENT:\n"
        f"{text}"
    )

    ai_audit_id = str(uuid.uuid4())

    source: str
    raw_summary: str
    metadata: dict[str, Any] = {}

    try:
        llm_result = await llm_client.generate_notary_summary(prompt, tenant_id=tenant_id)
        raw_summary = llm_result.raw_text
        source = "llm"
        metadata.update(
            {
                "model": llm_result.model,
                "latency_ms": llm_result.latency_ms,
            }
        )
    except (LLMError, Exception) as exc:  # noqa: BLE001
        logger.warning("ai_flow.notary_summarize_llm_failed", error=str(exc))
        source = "fallback"
        raw_summary = (
            "Automatische samenvatting niet beschikbaar. "
            "Dit is een veilige, generieke samenvatting op basis van de aangeleverde tekst. "
            "Controleer handmatig de inhoud van de akte."
        )
        metadata.update({"fallback_reason": str(exc)})

    summary = NotarySummary(
        title="Samenvatting notariële akte",
        key_points=[raw_summary[:200]],
        parties_involved=[],
        risks_or_warnings=[],
        raw_summary=raw_summary,
    )

    response = NotarySummarizeResponse(
        document_id=payload.document_id,
        summary=summary,
        source=source,
        metadata=metadata,
    )

    audit = AiCallAudit(
        id=ai_audit_id,
        tenant_id=tenant_id,
        flow_name="notary_summarize",
        request_payload=payload.model_dump(),
        response_payload=response.model_dump(),
        success=True,
    )
    try:
        db.add(audit)
        await db.commit()
    except Exception as exc:  # noqa: BLE001
        logger.warning("ai_flow.audit_persist_failed", error=str(exc))
        await db.rollback()

    return response

