# AI Platform

Multi-tenant AI platform with FastAPI and Python. Uses `X-Tenant-ID` for tenant context, a single LLM client with timeouts/retries, and audit logging for AI calls. SQLite by default; swap to Postgres via env.

**Run:**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Notary summarize example:**

```bash
curl -X POST "http://localhost:8000/api/v1/ai/notary/summarize" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: tenant-123" \
  -d '{"text": "Document text here...", "language": "nl"}'
```

If the LLM is down or returns bad data, the API responds with a safe fallback summary. Add more flows in `app/services_ai_flows.py`, wire a real model in `app/services_llm.py`, and use Alembic when you move off SQLite.
