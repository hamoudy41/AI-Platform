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
cd api
docker build -t ai-platform-api .
```
