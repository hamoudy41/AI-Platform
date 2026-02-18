# Compliance & Privacy

Data handling, security, audit, and operational controls for regulated deployments of AgentHub.

---

## Table of Contents

1. [Data Handling](#1-data-handling)
2. [Audit Trail](#2-audit-trail)
3. [Security](#3-security)
4. [Privacy](#4-privacy)
5. [Operational Controls](#5-operational-controls)
6. [Checklist](#6-checklist)

---

## 1. Data Handling

### 1.1 Tenant Isolation

All data is scoped by `tenant_id`. The tenant is derived from the `X-Tenant-ID` header (default: `default`). No cross-tenant access: documents, document chunks, and AI audit records are filtered by `tenant_id` in every query.

### 1.2 Data Storage

| Data | Storage | Retention |
|------|---------|-----------|
| Documents | PostgreSQL / SQLite | Until explicitly deleted |
| Document chunks (RAG) | PostgreSQL / SQLite | Until document deleted or re-indexed |
| AI call audit | PostgreSQL / SQLite | Configurable via `AI_AUDIT_RETENTION_DAYS` |
| Document cache | Redis (optional) | 300 seconds TTL |

### 1.3 LLM Data Transmission

- **Ollama / local**: Text is sent to the configured LLM endpoint (e.g. `http://localhost:11434`). Data remains on your infrastructure.
- **OpenAI-compatible (external)**: Text is sent to the configured URL (e.g. `https://api.openai.com/v1`). Data is transmitted to the third-party provider. Review their privacy policy and DPA before use.

### 1.4 Search Tool

The agent's search tool uses DuckDuckGo (default) or Tavily. Query text is sent to these providers. DuckDuckGo does not require an API key; Tavily requires `TAVILY_API_KEY`.

---

## 2. Audit Trail

### 2.1 AI Call Audit

Every AI flow (notary, classify, ask, RAG query, agent chat) logs to `ai_call_audit`:

| Column | Description |
|--------|-------------|
| `id` | UUID |
| `tenant_id` | Tenant context |
| `flow_name` | e.g. `notary_summarize`, `classify`, `ask`, `rag_query`, `agent_chat` |
| `request_payload` | JSON of request (text, question, etc.) |
| `response_payload` | JSON of response (answer, label, etc.) or null on failure |
| `success` | Boolean |
| `created_at` | Timestamp |

App-level only. Database access logs and infrastructure audits are outside this scope.

### 2.2 Retention and Purge

Set `AI_AUDIT_RETENTION_DAYS` (e.g. 90) to define retention. Purge is not automatic; run:

```bash
cd api
python -m app.audit
```

Recommended: cron job, e.g. daily at 02:00:

```
0 2 * * * cd /path/to/api && python -m app.audit
```

---

## 3. Security

### 3.1 API Authentication

When `API_KEY` is set (required in `ENVIRONMENT=prod`):

- All requests to `/api/v1/*` and `/metrics` must include `X-API-Key: <API_KEY>`.
- `/health` is exempt for load balancer health checks.
- Invalid or missing key returns 401 Unauthorized.

### 3.2 Security Headers

The API adds:

| Header | Value |
|--------|-------|
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| Referrer-Policy | strict-origin-when-cross-origin |
| Strict-Transport-Security | max-age=31536000; includeSubDomains (prod only) |

### 3.3 CORS

Configure `CORS_ALLOWED_ORIGINS` in production. Default `*` allows any origin. Use comma-separated frontend URLs.

### 3.4 TLS and Secrets

- Use TLS in production. Enforce HTTPS at the load balancer or reverse proxy.
- Store secrets (API keys, DB credentials) in environment variables or a secrets manager. Do not commit `.env` to version control.

---

## 4. Privacy

### 4.1 Data Subject Rights

Tenant-scoped data. Implement access and deletion (e.g. GDPR Article 15, 17) at the application or API gateway level. The platform does not provide built-in data subject request workflows.

### 4.2 Data Minimization

Only fields necessary for each flow are sent to the LLM. Responses include `source` and metadata for transparency.

### 4.3 PII

The platform does not perform PII detection or redaction. If handling PII, consider:

- Pre-processing to redact before LLM calls
- Post-processing to redact in responses
- External tools (e.g. Presidio) as middleware

---

## 5. Operational Controls

### 5.1 Rate Limiting

When `REDIS_URL` is set, per-tenant rate limiting applies to all `/api/v1/*` endpoints. Default: 120 requests per minute per tenant. Configurable via `RATE_LIMIT_PER_MINUTE`. Returns 429 when exceeded.

### 5.2 Health and Metrics

- **Health**: `GET /api/v1/health` returns `db_ok`, `redis_ok`, `llm_ok` for dependency status.
- **Metrics**: `GET /metrics` exposes Prometheus metrics. Requires `X-API-Key` when `API_KEY` is set.

### 5.3 Logging

Structured logging via structlog. `request_id` bound per request. Log level configurable via `LOG_LEVEL`.

---

## 6. Checklist

| Area | Status | Notes |
|------|--------|-------|
| Tenant isolation | Done | All queries filtered by tenant_id |
| Audit trail | Done | ai_call_audit for all AI flows |
| API auth | Required in prod | API_KEY + X-API-Key |
| Rate limiting | Redis | Per-tenant, configurable |
| Monitoring | Done | Prometheus metrics, health endpoint |
| Retention | Configurable | AI_AUDIT_RETENTION_DAYS + cron |
| Third-party LLM | Operator responsibility | Review provider DPA and privacy |
| CORS | Configurable | Restrict in prod |
| TLS | Operator responsibility | Enforce at infra layer |
