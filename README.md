# AI Platform

Multi-tenant AI platform with FastAPI and Python. Uses `X-Tenant-ID` for tenant context, a single LLM client with timeouts/retries, and audit logging for AI calls. Supports **Ollama** (local open-source models) and **OpenAI-compatible** APIs (e.g. vLLM, LocalAI, OpenAI). SQLite by default; swap to Postgres via env.

**Run:**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Use real open-source models (Ollama):**

1. Install [Ollama](https://ollama.com) and run a model, e.g. `ollama run llama3.2`
2. Set env and start the app:

```bash
export LLM_PROVIDER=ollama
export LLM_BASE_URL=http://localhost:11434
export LLM_MODEL=llama3.2
uvicorn app.main:app --reload
```

**OpenAI-compatible (vLLM, LocalAI, or OpenAI):**

```bash
export LLM_PROVIDER=openai_compatible
export LLM_BASE_URL=http://localhost:8000   # or https://api.openai.com/v1
export LLM_MODEL=llama-3.2-3b
# optional: export LLM_API_KEY=sk-...
uvicorn app.main:app --reload
```

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/ai/notary/summarize` | Summarize notarial-style document (body: `text`, optional `document_id`, `language`) |
| POST | `/api/v1/ai/classify` | Classify text into one of given labels (body: `text`, optional `candidate_labels`) |
| POST | `/api/v1/ai/ask` | Answer a question given a context (body: `question`, `context`) |
| GET  | `/api/v1/health` | Health check |
| POST | `/api/v1/documents` | Create document (body: `id`, `title`, `text`) |
| GET  | `/api/v1/documents/{id}` | Get document by id |

If the LLM is unavailable, notary summarization and classify/ask return safe fallbacks. Add more flows in `app/services_ai_flows.py` and use Alembic when you move off SQLite.
