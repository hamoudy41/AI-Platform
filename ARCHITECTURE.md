# Architecture

Technical architecture and roadmap for the AI Platform.

---

## 1. Current Architecture

### 1.1 Overview

| Layer | Implementation |
|-------|----------------|
| **Backend** | FastAPI, async SQLAlchemy, SQLite or Postgres |
| **AI** | Ollama / OpenAI-compatible LLM, streaming |
| **Agents** | LangGraph ReAct agent (calculator, search, document lookup) |
| **RAG** | Chunking, embeddings (mock or API), vector retrieval |
| **Flows** | Notary summarize, classify, ask, RAG query, agent chat |
| **Frontend** | React, Vite, Tailwind, streaming UI |
| **Infra** | Docker Compose, Kubernetes manifests |
| **Observability** | Prometheus metrics, `ai_call_audit` |

### 1.2 High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (React)                                                │
│  Health | Documents | RAG | Agents | Classify | Notary | Ask     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  API (FastAPI)                                                   │
│  Auth | Rate Limit | Tenant | CORS | Security Headers           │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Agent        │     │  RAG            │     │  AI Flows       │
│  LangGraph    │     │  Chunking +     │     │  Notary,        │
│  Tools        │     │  Embeddings +   │     │  Classify, Ask  │
│  ReAct        │     │  Retrieval      │     │                 │
└───────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  LLM (Ollama / OpenAI-compatible)                                │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  PostgreSQL   │     │  Redis          │     │  Document Chunks │
│  Documents    │     │  Rate Limit     │     │  (embeddings)    │
│  ai_call_audit│     │  Cache          │     │                 │
└───────────────┘     └─────────────────┘     └─────────────────┘
```

### 1.3 Directory Structure

```
api/
├── app/
│   ├── agents/           # LangGraph ReAct agent
│   │   ├── react_agent.py
│   │   └── tools/        # calculator, search, document_lookup
│   ├── rag/              # Chunking, embeddings, retrieval
│   ├── api.py            # Routes, middleware
│   ├── services_ai_flows.py
│   ├── services_llm.py
│   └── services_rag.py
├── tests/
frontend/
├── src/
│   ├── components/tabs/  # HealthTab, AgentTab, RAGTab, etc.
│   └── api.ts
```

### 1.4 Key Design Decisions

- **Modular monolith**: Single API process; agents, RAG, and flows in-process.
- **Tenant isolation**: All data scoped by `X-Tenant-ID`.
- **Streaming**: SSE for ask, RAG query, and agent chat.
- **Search**: DuckDuckGo (default) or Tavily via `SEARCH_PROVIDER`.

---

## 2. Roadmap

Planned enhancements (not yet implemented):

| Area | Planned |
|------|---------|
| **Observability** | Langfuse / OpenTelemetry tracing |
| **Evaluations** | Regression suite, LLM-as-judge |
| **Guardrails** | Content filter, PII redaction |
| **Task queue** | Celery/ARQ for async evals, batch indexing |
| **Vector store** | pgvector (currently JSON in document_chunks) |

---

## 3. References

- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [pgvector](https://github.com/pgvector/pgvector)
