from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Health check endpoint."""

    settings = get_settings()
    return HealthResponse(
        status="ok",
        environment=settings.env,
        timestamp=datetime.utcnow(),
    )
