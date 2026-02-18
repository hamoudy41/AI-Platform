# API

FastAPI backend. See [README](../README.md) for setup.

```bash
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

Docker: `docker build -t ai-platform-api .` from this directory.
