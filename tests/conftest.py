from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.api import create_app
from app.db import get_engine
from app.models import AiCallAudit, Base, Document


@pytest.fixture(autouse=True)
async def _clean_db():
    """Ensure tables exist and clear documents + audit before each test for isolation."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(delete(AiCallAudit))
        await conn.execute(delete(Document))
    yield


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def tenant_headers():
    return {"X-Tenant-ID": "tenant-1"}
