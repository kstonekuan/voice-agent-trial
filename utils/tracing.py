"""OpenTelemetry tracing configuration for voice agent platform."""

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from pipecat.utils.tracing.setup import setup_tracing as pipecat_setup_tracing

from config.settings import Settings
from utils.logger import logger


def setup_tracing(settings: Settings) -> None:
    """
    Initialize OpenTelemetry tracing with configured exporter.

    Args:
        settings: Application settings containing tracing configuration
    """
    if not settings.otel_enabled:
        logger.info("OpenTelemetry tracing is disabled")
        return

    logger.info(
        f"Initializing OpenTelemetry tracing: service={settings.otel_service_name}, "
        f"endpoint={settings.otel_exporter_otlp_endpoint}"
    )

    # Create OTLP gRPC exporter for Jaeger
    exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint,
        insecure=True,  # Use insecure connection for local development
    )

    # Initialize Pipecat's tracing setup
    pipecat_setup_tracing(
        service_name=settings.otel_service_name,
        exporter=exporter,
        console_export=False,  # Disable console export to reduce log verbosity
    )

    logger.info("OpenTelemetry tracing initialized successfully")
