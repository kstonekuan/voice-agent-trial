"""Cartesia Speech-to-Text service initialization."""

from loguru import logger
from pipecat.services.cartesia.stt import CartesiaSTTService

from config.settings import Settings


def create_stt_service(settings: Settings) -> CartesiaSTTService:
    """
    Initialize Cartesia Ink-Whisper STT service with optimized settings.

    Args:
        settings: Application settings

    Returns:
        Configured CartesiaSTTService instance
    """
    logger.info(
        "initializing_cartesia_stt",
    )
    return CartesiaSTTService(
        api_key=settings.cartesia_api_key,
    )
