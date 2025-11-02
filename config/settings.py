"""Configuration management for voice agent platform."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Settings:
    """Application configuration settings loaded from environment variables."""

    # API Keys
    cartesia_api_key: str
    cerebras_api_key: str
    elevenlabs_api_key: str
    daily_api_key: str | None = None
    daily_room_url: str | None = None
    daily_token: str | None = None

    # Transport Configuration
    transport_type: str = "websocket"  # "websocket" or "daily"
    ws_host: str = "localhost"
    ws_port: int = 8765

    # Voice Agent Configuration
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    llm_model: str = "llama-3.3-70b"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 150
    audio_sample_rate: int = 16000
    tts_optimize_latency: int = 3

    # Logging
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        """
        Load settings from environment variables.

        Returns:
            Settings instance populated from environment

        Raises:
            ValueError: If required environment variables are missing
        """
        # Load .env file if it exists
        env_file = Path.cwd() / ".env"
        if env_file.exists():
            load_dotenv(env_file)

        # Required API keys
        cartesia_api_key = os.getenv("CARTESIA_API_KEY")
        cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

        # Validate required keys
        missing_keys = []
        if not cartesia_api_key:
            missing_keys.append("CARTESIA_API_KEY")
        if not cerebras_api_key:
            missing_keys.append("CEREBRAS_API_KEY")
        if not elevenlabs_api_key:
            missing_keys.append("ELEVENLABS_API_KEY")

        if missing_keys:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_keys)}\\n"
                "Please create a .env file based on .env.example and add your API keys."
            )

        # Transport configuration
        transport_type = os.getenv("TRANSPORT_TYPE", "websocket")

        # Daily-specific validation
        daily_api_key = os.getenv("DAILY_API_KEY")
        daily_room_url = os.getenv("DAILY_ROOM_URL")
        daily_token = os.getenv("DAILY_TOKEN")

        if transport_type == "daily" and not all([daily_room_url, daily_token]):
            raise ValueError(
                "When TRANSPORT_TYPE=daily, you must provide "
                "DAILY_ROOM_URL and DAILY_TOKEN environment variables."
            )

        return cls(
            # API Keys
            cartesia_api_key=cartesia_api_key,
            cerebras_api_key=cerebras_api_key,
            elevenlabs_api_key=elevenlabs_api_key,
            daily_api_key=daily_api_key,
            daily_room_url=daily_room_url,
            daily_token=daily_token,
            # Transport
            transport_type=transport_type,
            ws_host=os.getenv("WS_HOST", "localhost"),
            ws_port=int(os.getenv("WS_PORT", "8765")),
            # Voice Agent
            elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
            llm_model=os.getenv("LLM_MODEL", "llama-3.3-70b"),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "150")),
            audio_sample_rate=int(os.getenv("AUDIO_SAMPLE_RATE", "16000")),
            tts_optimize_latency=int(os.getenv("TTS_OPTIMIZE_LATENCY", "3")),
            # Logging
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def validate(self) -> None:
        """
        Validate configuration settings.

        Raises:
            ValueError: If settings contain invalid values
        """
        # Validate transport type
        if self.transport_type not in ["websocket", "daily"]:
            raise ValueError(
                f"Invalid TRANSPORT_TYPE: {self.transport_type}. Must be 'websocket' or 'daily'."
            )

        # Validate numeric ranges
        if not 0.0 <= self.llm_temperature <= 2.0:
            raise ValueError("LLM_TEMPERATURE must be between 0.0 and 2.0")

        if self.llm_max_tokens < 1:
            raise ValueError("LLM_MAX_TOKENS must be positive")

        if self.tts_optimize_latency not in range(5):
            raise ValueError("TTS_OPTIMIZE_LATENCY must be between 0 and 4")

        if self.audio_sample_rate not in [8000, 16000, 22050, 24000, 44100, 48000]:
            raise ValueError(
                f"Unsupported AUDIO_SAMPLE_RATE: {self.audio_sample_rate}. "
                "Common values: 8000, 16000, 22050, 24000, 44100, 48000"
            )


def load_settings() -> Settings:
    """
    Load and validate application settings.

    Returns:
        Validated Settings instance

    Raises:
        ValueError: If configuration is invalid or incomplete
    """
    settings = Settings.from_env()
    settings.validate()
    return settings
