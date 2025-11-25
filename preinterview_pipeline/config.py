"""Configuration for preinterview pipeline."""
from __future__ import annotations

import os
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # API Configuration
    api_title: str = "Preinterview Pipeline API"
    api_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Logging
    log_level: str = "INFO"

    # External APIs
    github_token: Optional[str] = None
    linkedin_api_key: Optional[str] = None

    # Rate Limiting
    rate_limit_delay: float = 1.0  # seconds between API calls
    max_retries: int = 3
    retry_backoff: float = 2.0

    # Parsing
    max_file_size_mb: int = 50
    supported_resume_formats: list[str] = ["pdf", "docx", "doc"]

    # Database (for future use)
    database_url: Optional[str] = None

    # CORS
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


# Default settings instance
settings = get_settings()
