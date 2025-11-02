"""Cartesia Speech-to-Text service initialization."""

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
    stt = CartesiaSTTService(
        api_key=settings.cartesia_api_key,
        sample_rate=settings.audio_sample_rate,
    )

    return stt
