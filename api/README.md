# AI Platform API

FastAPI backend. See root [README](../README.md) for full setup.

## Local dev

```bash
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

## Docker

```bash
# From repo root; build frontend first
docker build -t ai-platform-frontend -f ../frontend/Dockerfile ../frontend
docker build -t ai-platform .
```
