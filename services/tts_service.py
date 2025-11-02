"""ElevenLabs Text-to-Speech service initialization."""

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
    tts = ElevenLabsTTSService(
        api_key=settings.elevenlabs_api_key,
        voice_id=settings.elevenlabs_voice_id,
        model="eleven_flash_v2_5",  # Fastest model
        optimize_streaming_latency=settings.tts_optimize_latency,
        sample_rate=settings.audio_sample_rate,
    )

    return tts
