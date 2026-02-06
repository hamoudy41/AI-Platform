from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .core.config import get_settings
from .core.logging import get_logger


logger = get_logger(__name__)


class LLMError(Exception):
    pass


@dataclass
class LLMResult:
    raw_text: str
    model: str
    latency_ms: float
    used_fallback: bool = False


class LLMClient:
    def __init__(self) -> None:
        self._settings = get_settings()

    async def generate_notary_summary(self, prompt: str, *, tenant_id: str) -> LLMResult:
        if not self._settings.llm_base_url:
            logger.info(
                "llm.mock_notary_summary",
                tenant_id=tenant_id,
            )
            return LLMResult(
                raw_text="Summary of the notarial document.",
                model="mock",
                latency_ms=5.0,
                used_fallback=False,
            )

        return await self._call_llm(
            path="/notary/summarize",
            json={"prompt": prompt, "tenant_id": tenant_id},
        )

    @retry(wait=wait_exponential(min=0.5, max=5), stop=stop_after_attempt(get_settings().llm_max_retries))
    async def _call_llm(self, path: str, json: Mapping[str, Any]) -> LLMResult:
        assert self._settings.llm_base_url is not None, "llm_base_url must be configured"

        url = f"{self._settings.llm_base_url}{path}"
        timeout = self._settings.llm_timeout_seconds

        logger.info("llm.request", url=url, timeout=timeout)

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(
                    url,
                    json=json,
                    headers={"Authorization": f"Bearer {self._settings.llm_api_key or ''}"},
                )
            except httpx.RequestError as exc:
                logger.warning("llm.transport_error", error=str(exc))
                raise LLMError("LLM transport error") from exc

        if response.status_code != 200:
            logger.warning("llm.bad_status", status=response.status_code, body=response.text)
            raise LLMError(f"LLM returned HTTP {response.status_code}")

        data: Optional[dict[str, Any]] = None
        try:
            data = response.json()
        except ValueError as exc:
            logger.warning("llm.invalid_json", body=response.text)
            raise LLMError("LLM returned invalid JSON") from exc

        text = data.get("text")
        model = data.get("model", "unknown")
        latency_ms = float(data.get("latency_ms", 0.0))

        if not isinstance(text, str) or not text.strip():
            logger.warning("llm.empty_text", data=data)
            raise LLMError("LLM returned empty text")

        return LLMResult(raw_text=text, model=model, latency_ms=latency_ms)


llm_client = LLMClient()

