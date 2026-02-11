from __future__ import annotations

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter("ai_platform_requests_total", "Total requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram(
    "ai_platform_request_duration_seconds",
    "Request latency",
    ["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
LLM_CALLS = Counter("ai_platform_llm_calls_total", "LLM API calls", ["flow", "source"])


def get_metrics() -> bytes:
    return generate_latest()


def metrics_content_type() -> str:
    return CONTENT_TYPE_LATEST
