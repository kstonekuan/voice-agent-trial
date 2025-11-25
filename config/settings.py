"""Configuration management for voice agent platform using Pydantic Settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # API Keys - Required
    cartesia_api_key: str = Field(..., description="Cartesia API key for STT service")
    cerebras_api_key: str = Field(..., description="Cerebras API key for LLM service")
    elevenlabs_api_key: str = Field(..., description="ElevenLabs API key for TTS service")

    # API Keys - Required (Daily)
    daily_api_key: str = Field(..., description="Daily.co API key")

    # Voice Agent Configuration
    elevenlabs_voice_id: str = Field(
        "21m00Tcm4TlvDq8ikWAM", description="ElevenLabs voice ID (default: Rachel)"
    )

    # Logging
    log_level: str = Field("INFO", description="Logging level")

    # OpenTelemetry Tracing
    otel_enabled: bool = Field(False, description="Enable OpenTelemetry tracing")
    otel_exporter_otlp_endpoint: str = Field(
        "http://localhost:4317", description="OTLP gRPC endpoint for trace export"
    )
    otel_service_name: str = Field("voice-agent", description="Service name for tracing")

    # Network Statistics Monitoring
    network_stats_enabled: bool = Field(
        True, description="Enable network statistics monitoring and CSV logging"
    )
    network_stats_output_dir: Path = Field(
        Path("data/network_stats"),
        description="Directory for network statistics CSV output files",
    )

    # Voice Dictation Configuration
    dictation_hotkey: str = Field(
        "ctrl_r", description="Hotkey for push-to-talk dictation (ctrl_r, alt_r, etc.)"
    )
    dictation_typing_speed: float = Field(
        0.0, description="Delay between characters when typing (0 = instant)"
    )
    dictation_show_preview: bool = Field(True, description="Show transcription preview in terminal")
