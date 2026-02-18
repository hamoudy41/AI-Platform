# API

FastAPI backend for AgentHub. This document covers local development, testing, migrations, and deployment.

---

## Prerequisites

- Python 3.11+
- (Optional) PostgreSQL, Redis, Ollama for full functionality

---

## Local Development

### Setup

```bash
cd api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
```

Edit `.env` with your `LLM_PROVIDER`, `LLM_BASE_URL`, and `LLM_MODEL`. For SQLite (default), no database setup. For Postgres, set `DATABASE_URL`.

### Run

```bash
alembic upgrade head   # first run
uvicorn app.main:app --reload
```

API at http://localhost:8000. Docs at http://localhost:8000/docs.

### Hot Reload

`--reload` watches `app/` and `alembic/`; uvicorn restarts on file changes.

---

## Testing

```bash
cd api
pytest tests/ -v
```

Tests must run from `api/` so the `app` package resolves. Use `tests/` as path.

### Coverage

```bash
pytest tests/ -v --cov=app --cov-report=term-missing --cov-branch --cov-fail-under=80
```

Coverage thresholds: 80% for statements, branches, functions, lines.

### Test Structure

- `conftest.py`: Fixtures, `httpx` mock for LLM
- `test_*.py`: Per-module tests
- AI endpoints: mock `llm_client` or `httpx`; no real LLM calls

---

## Database Migrations

### Create Migration

```bash
alembic revision -m "add_foo_column" --autogenerate
```

Review `alembic/versions/*.py` before applying. Autogenerate may miss renames or data migrations.

### Apply

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

---

## Linting & Formatting

```bash
ruff check app tests --fix
ruff format app tests
```

Pre-commit: `pre-commit install` runs ruff on commit.

---

## Deployment

### Docker

```bash
docker build -t ai-platform-api .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  -e LLM_PROVIDER=ollama \
  -e LLM_BASE_URL=http://ollama:11434 \
  ai-platform-api
```

Or use `docker compose` from repo root.

### Environment

Production requires:

- `ENVIRONMENT=prod`
- `API_KEY` (non-empty)
- `DATABASE_URL` (Postgres recommended)
- `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_MODEL`

Optional: `REDIS_URL` for rate limiting and document cache.

---

## Module Overview

| Module | Purpose |
|--------|---------|
| `app/main.py` | FastAPI app entry |
| `app/api.py` | Routes, middleware, lifespan |
| `app/db.py` | Async engine, session factory |
| `app/models.py` | SQLAlchemy models |
| `app/schemas.py` | Pydantic request/response |
| `app/services_llm.py` | LLM client (Ollama, OpenAI-compatible) |
| `app/services_ai_flows.py` | Notary, classify, ask flows |
| `app/services_rag.py` | RAG query flow |
| `app/agents/react_agent.py` | LangGraph ReAct agent |
| `app/agents/tools/` | Calculator, search, document lookup |
| `app/rag/` | Chunking, embeddings, pipeline |
| `app/core/` | Config, logging, metrics, Redis |
| `app/audit.py` | AI audit retention purge |
