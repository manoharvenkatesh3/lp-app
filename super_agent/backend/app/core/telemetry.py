from __future__ import annotations

from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def setup_tracing(settings: Settings) -> None:
    """Configure OpenTelemetry tracing if an exporter endpoint is provided."""

    if not settings.enable_telemetry or not settings.otel_exporter_otlp_endpoint:
        logger.info("telemetry.disabled", reason="missing OTLP endpoint")
        return

    resource = Resource.create({
        "service.name": settings.name,
        "service.environment": settings.env,
    })

    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
    )
    provider.add_span_processor(processor)
    set_tracer_provider(provider)
    trace.set_tracer_provider(provider)
    logger.info("telemetry.enabled", endpoint=settings.otel_exporter_otlp_endpoint)


def instrument_app(app: Any) -> None:
    """Instrument FastAPI application with OpenTelemetry."""

    try:
        FastAPIInstrumentor.instrument_app(app)
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.warning("telemetry.instrumentation_failed", error=str(exc))
