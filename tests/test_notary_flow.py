from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.api import create_app


@pytest.mark.asyncio
async def test_notary_summarize_flow_mock_llm() -> None:
    app = create_app()

    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "text": "Dit is een voorbeeldakte.",
            "language": "nl",
        }
        response = await client.post(
            "/api/v1/ai/notary/summarize",
            headers={"X-Tenant-ID": "tenant-1"},
            json=payload,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["source"] in {"llm", "fallback"}
    assert "summary" in data
    assert "title" in data["summary"]
    assert isinstance(data["summary"]["key_points"], list)

