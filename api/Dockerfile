# Deprecated: Use root ./Dockerfile for Docker Compose and CI (single multi-stage build).
# Backend. Requires ai-platform-frontend image (build frontend first).
FROM ai-platform-frontend AS frontend

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[dev]"

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY --from=frontend /dist /app/static

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
