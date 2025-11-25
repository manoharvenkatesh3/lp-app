from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[2].parent / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
    )

    # Core application
    name: str = "Super Agent API"
    env: Literal["local", "staging", "prod"] = "local"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql+psycopg2://superagent:superagent@postgres:5432/superagent"

    # Observability
    enable_telemetry: bool = True
    otel_exporter_otlp_endpoint: str | None = None

    # Third-party integrations
    openrouter_api_key: str | None = None
    deepgram_api_key: str | None = None
    zoom_client_id: str | None = None
    zoom_client_secret: str | None = None
    google_meet_service_account: str | None = None
    teams_tenant_id: str | None = None
    teams_client_secret: str | None = None
    ats_api_key: str | None = None
    ats_base_url: str | None = None

    # Vector configuration
    vector_dimension: int = 1536


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
