# Postman – AgentHub

Postman collection and environment for testing the AgentHub API.

---

## Import

1. **Collection:** File → Import → select `AI-Platform.postman_collection.json`
2. **Environment (optional):** File → Import → select `AI-Platform.postman_environment.json`, then select "AI Platform – Local" in the environment dropdown

---

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `base_url` | `http://localhost:8000` | API base URL |
| `api_prefix` | `/api/v1` | API path prefix |
| `tenant_id` | `tenant-123` | Value for `X-Tenant-ID` header |
| `api_key` | — | Value for `X-API-Key` (required when API_KEY set in prod) |
| `doc_id` | Auto per run | Unique document ID; set by Create prerequest script |

---

## Endpoints

| Group | Method | Path | Description |
|-------|--------|------|-------------|
| Health | GET | `/health` | Health check (db, redis, llm status) |
| Documents | POST | `/documents` | Create document |
| Documents | GET | `/documents/{{doc_id}}` | Get document by ID |
| Documents | POST | `/documents/upload` | Upload file (multipart) |
| AI – Notary | POST | `/ai/notary/summarize` | Summarize text or document |
| AI – Classify | POST | `/ai/classify` | Zero-shot classification |
| AI – Ask | POST | `/ai/ask` | Q&A over context |
| AI – Ask | POST | `/ai/ask/stream` | Q&A streaming (SSE) |
| AI – RAG | POST | `/ai/rag/index` | Index document for RAG |
| AI – RAG | POST | `/ai/rag/query` | RAG query |
| AI – RAG | POST | `/ai/rag/query/stream` | RAG query streaming (SSE) |
| AI – Agent | POST | `/ai/agents/chat` | ReAct agent chat |
| AI – Agent | POST | `/ai/agents/chat/stream` | Agent chat streaming (SSE) |

---

## Run Order

1. Start the API: `uvicorn app.main:app --reload` (from `api/`)
2. Run the collection. The Create document request uses a unique `doc_id` per run to avoid duplicate-key errors.
3. Summarize (by document_id), RAG index, and RAG query depend on an existing document; create one first.
