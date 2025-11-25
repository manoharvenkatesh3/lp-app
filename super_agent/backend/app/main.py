from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.healthz import router as health_router
from app.api.routes import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.telemetry import instrument_app, setup_tracing


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    setup_tracing(settings)

    app = FastAPI(title=settings.name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    instrument_app(app)

    app.include_router(health_router, tags=["health"])
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
