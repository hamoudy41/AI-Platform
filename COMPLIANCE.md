# Compliance & Privacy

Data handling, security, and operational controls for regulated deployments.

## Data

- **Tenant isolation**: All data filtered by `tenant_id`; no cross-tenant access. Documents and AI audit stored in DB.
- **LLM calls**: Text is sent to configured backend (Ollama, vLLM, etc.). Local backends keep data on your infra; `openai_compatible` with external URL sends data to that provider.
- **Retention**: Documents kept until deleted. `ai_call_audit` stores payloads for traceability; define purge policies per tenant.

## Audit

Every AI call is logged to `ai_call_audit` (`tenant_id`, `flow_name`, `success`, `request_payload`, `response_payload`). App-level only; DB/access audits are infra-specific.

## Security

- Optional API key via `API_KEY`; `X-Tenant-ID` for tenant.
- TLS and secrets: use env/secrets manager; enforce HTTPS in production.

## Privacy

Tenant-scoped data; implement data subject rights (access, deletion) at app or gateway. Only required fields sent to LLM. Responses include `source` and metadata for transparency.

## Ops

- Metrics: `/metrics`; health: `/api/v1/health` (includes `db_ok`).
- Redis (`REDIS_URL`): per-tenant rate limit (default 120/min).

## Checklist

| Area            | Status     |
|-----------------|------------|
| Tenant isolation| Done       |
| Audit trail     | Done       |
| API auth        | Optional   |
| Rate limiting   | Redis      |
| Monitoring      | Done       |
| Retention       | Per tenant |
| Third-party LLM | Operator   |
