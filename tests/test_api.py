from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "environment" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_tenant_default_when_no_header(client):
    r = await client.post(
        "/api/v1/documents",
        json={"id": "d1", "title": "T", "text": "body"},
    )
    assert r.status_code == 201
    assert r.json()["id"] == "d1"


@pytest.mark.asyncio
async def test_documents_create_and_get(client, tenant_headers):
    r = await client.post(
        "/api/v1/documents",
        headers=tenant_headers,
        json={"id": "doc-1", "title": "Title", "text": "Content"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["id"] == "doc-1"
    assert data["title"] == "Title"
    assert data["text"] == "Content"
    assert "created_at" in data

    r2 = await client.get("/api/v1/documents/doc-1", headers=tenant_headers)
    assert r2.status_code == 200
    assert r2.json()["text"] == "Content"


@pytest.mark.asyncio
async def test_documents_get_404_wrong_tenant(client, tenant_headers):
    await client.post(
        "/api/v1/documents",
        headers=tenant_headers,
        json={"id": "doc-2", "title": "T", "text": "X"},
    )
    r = await client.get(
        "/api/v1/documents/doc-2",
        headers={"X-Tenant-ID": "other-tenant"},
    )
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_documents_get_404_missing(client, tenant_headers):
    r = await client.get(
        "/api/v1/documents/nonexistent",
        headers=tenant_headers,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_notary_summarize_with_document_id(client, tenant_headers):
    await client.post(
        "/api/v1/documents",
        headers=tenant_headers,
        json={"id": "ndoc", "title": "N", "text": "Notary document body here."},
    )
    r = await client.post(
        "/api/v1/ai/notary/summarize",
        headers=tenant_headers,
        json={"document_id": "ndoc", "text": "ignored", "language": "en"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["document_id"] == "ndoc"
    assert data["source"] in {"llm", "fallback"}
    assert "summary" in data


@pytest.mark.asyncio
async def test_classify(client, tenant_headers):
    r = await client.post(
        "/api/v1/ai/classify",
        headers=tenant_headers,
        json={
            "text": "This is an invoice for 100 euros.",
            "candidate_labels": ["invoice", "letter", "contract"],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["label"] in ["invoice", "letter", "contract"]
    assert data["source"] in {"llm", "fallback"}
    assert "model" in data


@pytest.mark.asyncio
async def test_ask(client, tenant_headers):
    r = await client.post(
        "/api/v1/ai/ask",
        headers=tenant_headers,
        json={"question": "What is the total?", "context": "The total amount is 50 EUR."},
    )
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert data["source"] in {"llm", "fallback"}


@pytest.mark.asyncio
async def test_validation_error_returns_422(client, tenant_headers):
    r = await client.post(
        "/api/v1/ai/notary/summarize",
        headers=tenant_headers,
        json={},
    )
    assert r.status_code == 422
