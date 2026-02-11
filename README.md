# AI Platform

Multi-tenant FastAPI app. `X-Tenant-ID` for tenant context; Ollama or OpenAI-compatible LLM backends; SQLite or Postgres.

## Setup

```bash
# Backend
cd api && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

Configure `LLM_PROVIDER` and `LLM_BASE_URL` in `.env`. Optional `API_KEY` for `X-API-Key` auth.

## Deploy

```bash
docker compose up --build -d   # localhost:8000
kubectl apply -k k8s/
```

Compose: backend + Postgres + Redis. Pull model: `docker compose run ollama ollama pull llama3.1:8b`. For kind: `docker compose build backend` then `kind load docker-image ai-platform`.

## API

| Method | Path | Body |
|--------|------|------|
| GET | `/api/v1/health` | — |
| POST | `/api/v1/documents` | `id`, `title`, `text` |
| GET | `/api/v1/documents/{id}` | — |
| POST | `/api/v1/ai/notary/summarize` | `text`, optional `document_id`, `language` |
| POST | `/api/v1/ai/classify` | `text`, optional `candidate_labels` |
| POST | `/api/v1/ai/ask` | `question`, `context` |

Headers: `X-Tenant-ID` (default: `default`), optional `X-API-Key`. Metrics: `/metrics`. Postman: `postman/AI-Platform.postman_collection.json`.

## Dev

```bash
cd api
pytest tests/ -v                    # run tests
alembic upgrade head                # apply migrations
alembic revision -m "msg" --autogenerate  # new migration
ruff check app tests --fix          # lint + fix
ruff format app tests               # format
```

`api/` backend, `frontend/` React app, `k8s/` manifests. See `ARCHITECTURE.md`, `COMPLIANCE.md`, `frontend/README.md`.
