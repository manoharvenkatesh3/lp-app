from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check payload."""

    status: str
    environment: str
    timestamp: datetime


class PaginatedResponse(BaseModel):
    """Generic pagination schema."""

    total: int
    limit: int
    offset: int
