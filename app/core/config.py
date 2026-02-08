from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Platform"
    environment: Literal["local", "dev", "prod"] = "local"
    api_v1_prefix: str = "/api/v1"
    default_tenant_id: str = "default"
    tenant_header_name: str = "X-Tenant-ID"
    database_url: str = "sqlite+aiosqlite:///./app.db"
    llm_provider: Literal["ollama", "openai_compatible", ""] = ""
    llm_base_url: Optional[AnyHttpUrl] = None
    llm_api_key: Optional[str] = None
    llm_model: str = "llama3.2"
    llm_timeout_seconds: float = 60.0
    llm_max_retries: int = 2
    log_level: str = "INFO"
    enable_prometheus: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
