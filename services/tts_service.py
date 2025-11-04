"""ElevenLabs Text-to-Speech service initialization."""

from loguru import logger
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService

from config.settings import Settings


def create_tts_service(settings: Settings) -> ElevenLabsTTSService:
    """
    Initialize ElevenLabs Flash v2.5 TTS service with latency optimization.

    Args:
        settings: Application settings

    Returns:
        Configured ElevenLabsTTSService instance
    """

    logger.info(
        "initializing_elevenlabs_tts",
        voice_id=settings.elevenlabs_voice_id,
    )

    return ElevenLabsTTSService(
        api_key=settings.elevenlabs_api_key,
        voice_id=settings.elevenlabs_voice_id,
    )
