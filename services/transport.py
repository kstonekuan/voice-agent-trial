"""Transport layer factory for configurable WebSocket or Daily WebRTC."""

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.transports.base_transport import BaseTransport
from pipecat.transports.daily.transport import DailyParams, DailyTransport
from pipecat.transports.websocket.server import (
    WebsocketServerParams,
    WebsocketServerTransport,
)

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


def create_transport(settings: Settings) -> BaseTransport:
    """
    Create transport based on configuration (WebSocket or Daily WebRTC).

    Args:
        settings: Application settings

    Returns:
        Configured transport instance (WebSocket or Daily)

    Raises:
        ValueError: If transport type is invalid
    """
    # Create VAD analyzer (shared by both transports)
    vad = SileroVADAnalyzer()

    if settings.transport_type == "websocket":
        logger.info(
            "creating_websocket_transport",
            host=settings.ws_host,
            port=settings.ws_port,
        )
        return WebsocketServerTransport(
            host=settings.ws_host,
            port=settings.ws_port,
            params=WebsocketServerParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                add_wav_header=False,
                vad_analyzer=vad,
            ),
        )

    elif settings.transport_type == "daily":
        if not settings.daily_room_url or not settings.daily_token:
            raise ValueError("Daily transport requires DAILY_ROOM_URL and DAILY_TOKEN to be set")
        logger.info(
            "creating_daily_transport",
            room_url=settings.daily_room_url,
        )
        return DailyTransport(
            room_url=settings.daily_room_url,
            token=settings.daily_token,
            bot_name="Voice Agent",
            params=DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=vad,
                transcription_enabled=False,  # Using Cartesia STT instead
            ),
        )

    else:
        raise ValueError(
            f"Invalid transport type: {settings.transport_type}. Must be 'websocket' or 'daily'."
        )
