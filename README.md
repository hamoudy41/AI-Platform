# AI Platform

Multi-tenant AI platform with FastAPI. Uses `X-Tenant-ID` header for tenant context, audit logging for AI calls, and supports **Ollama** or **OpenAI-compatible** APIs (vLLM, LocalAI, OpenAI). SQLite by default; swap to Postgres via `DATABASE_URL`.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
cp .env.example .env   # edit .env for LLM backend
uvicorn app.main:app --reload
```

`.env` configures the LLM backend (Ollama, OpenAI-compatible, or leave empty for mock). If no provider is set, endpoints return mock/fallback responses.

## API

| Method | Path | Body |
|--------|------|------|
| GET | `/api/v1/health` | — |
| POST | `/api/v1/documents` | `id`, `title`, `text` |
| GET | `/api/v1/documents/{id}` | — |
| POST | `/api/v1/ai/notary/summarize` | `text`, optional `document_id`, `language` |
| POST | `/api/v1/ai/classify` | `text`, optional `candidate_labels` |
| POST | `/api/v1/ai/ask` | `question`, `context` |

Send `X-Tenant-ID` header (default: `default`). Import `postman/AI-Platform.postman_collection.json` for ready-made requests.

## Dev

```bash
pytest tests/ -v                    # run tests
ruff check app tests --fix          # lint + fix
ruff format app tests               # format
```
