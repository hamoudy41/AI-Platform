# Kubernetes Deployment

Kubernetes manifests for deploying AgentHub. Uses Kustomize for resource management.

---

## Prerequisites

- `kubectl` configured for your cluster
- Container images built and pushed to a registry (e.g. GHCR)

---

## Resources

| Resource | Purpose |
|----------|---------|
| `configmap.yaml` | Non-sensitive config (DATABASE_URL, REDIS_URL, ENVIRONMENT, etc.) |
| `postgres.yaml` | PostgreSQL StatefulSet and Service |
| `redis.yaml` | Redis Deployment and Service |
| `deployment.yaml` | API and UI Deployments, Services |
| `ingress.yaml` | (Optional) Ingress for external access |

---

## Configuration

### ConfigMap (`ai-platform-config`)

Edit `configmap.yaml` or override via Kustomize. Example data:

```yaml
data:
  DATABASE_URL: "postgresql+asyncpg://postgres:password@postgres:5432/aiplatform"
  REDIS_URL: "redis://redis:6379/0"
  ENVIRONMENT: "prod"
  ENABLE_PROMETHEUS: "true"
  API_V1_PREFIX: "/api/v1"
```

### Secrets (`ai-platform-secrets`)

Create a Secret for sensitive values. Not included in repo. Example:

```bash
kubectl create secret generic ai-platform-secrets \
  --from-literal=API_KEY=your-api-key \
  --from-literal=LLM_PROVIDER=ollama \
  --from-literal=LLM_BASE_URL=http://ollama:11434 \
  --from-literal=LLM_MODEL=llama3.2
```

For OpenAI-compatible:

```bash
kubectl create secret generic ai-platform-secrets \
  --from-literal=API_KEY=your-api-key \
  --from-literal=LLM_PROVIDER=openai_compatible \
  --from-literal=LLM_BASE_URL=https://api.openai.com/v1 \
  --from-literal=LLM_MODEL=gpt-4 \
  --from-literal=LLM_API_KEY=sk-xxx
```

Deployments use `envFrom` with `secretRef` (optional: true so startup works without secrets for non-LLM config).

---

## Apply

```bash
kubectl apply -k k8s/
```

To include Ingress, uncomment `ingress.yaml` in `kustomization.yaml`.

---

## Images

Deployments reference:

- `ghcr.io/hamoudy41/ai-platform-api:latest`
- `ghcr.io/hamoudy41/ai-platform-ui:latest`

Override via Kustomize `images` or edit `deployment.yaml`. Build and push via CI (`.github/workflows/cd.yml`).

---

## Init Container

The API deployment includes an init container that waits for Postgres:

```yaml
initContainers:
  - name: wait-for-db
    image: postgres:16-alpine
    command: ["sh", "-c", "until pg_isready -h postgres -U postgres; do sleep 2; done"]
```

Ensure the Postgres service is named `postgres` and reachable from the API pod.

---

## Probes

- **Liveness**: `GET /api/v1/health` on port 8000 (API), `GET /` on port 80 (UI)
- **Readiness**: Same as liveness for API
- **Initial delay**: 10s (API), 5s (UI)
