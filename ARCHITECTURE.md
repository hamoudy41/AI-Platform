# Architecture

## Overview

Multi-tenant AI platform for regulated environments. Backend-first design with FastAPI, tenant isolation via `X-Tenant-ID`, and LLM integration (Ollama / OpenAI-compatible) with fallbacks.

## Stack

| Layer      | Technology                                  |
|-----------|---------------------------------------------|
| API       | FastAPI                                     |
| DB        | SQLite (dev) / PostgreSQL (prod)            |
| ORM       | SQLAlchemy 2 (async)                        |
| Migrations| Alembic                                    |
| LLM       | Ollama, OpenAI-compatible (vLLM, LocalAI)   |
| Auth      | Optional API key (`X-API-Key`)              |
| Monitoring| Prometheus (`/metrics`)                      |

## Multi-tenancy

- **Tenant context**: `X-Tenant-ID` header (default: `default`)
- **Data separation**: `tenant_id` on all tenant-scoped tables; queries filter by tenant
- **Models**: `TenantScopedMixin` provides `tenant_id` column

## AI Flows

1. **Notary summarize** – Document summarization with structured output
2. **Classify** – Text classification into candidate labels
3. **Ask** – Q&A from provided context

Each flow:
- Calls LLM when configured; returns mock/fallback when not
- Audits to `ai_call_audit` (tenant, flow_name, success, payloads)
- Uses retries (tenacity) and timeouts

## Security

- **API key**: Set `API_KEY` in env to require `X-API-Key` on all API routes; `/metrics` and `/health` stay open
- **Health**: Includes DB connectivity check (`db_ok`)

## Deployment

- **Docker**: `docker build -t ai-platform .`
- **Compose**: `docker-compose up` (app + Postgres + Redis)
- **Kubernetes**: See `k8s/` (Deployment, Service, ConfigMap)
