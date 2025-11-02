#!/usr/bin/env python3
"""
Voice Agent Platform - CLI Application

A real-time voice assistant using:
- Cartesia Ink-Whisper (STT)
- Cerebras Llama 3.3-70B (LLM)
- ElevenLabs Flash v2.5 (TTS)
- Daily WebRTC or WebSocket (Transport)
"""

import asyncio
import os
from pathlib import Path

import typer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext

from config.settings import load_settings
from services.llm_service import create_llm_service
from services.stt_service import create_stt_service
from services.transport import create_transport
from services.tts_service import create_tts_service
from utils.logger import configure_logging, get_logger

__version__ = "0.1.0"

app = typer.Typer(
    name="voice-agent",
    help="Real-time voice agent platform with ultra-low latency",
    add_completion=False,
)


async def run_voice_agent(
    transport_type: str | None = None,
    env_file: Path | None = None,
    system_prompt: str | None = None,
    verbose: bool = False,
):
    """
    Main voice agent application logic.

    Args:
        transport_type: Transport type override (websocket or daily)
        env_file: Custom .env file path
        system_prompt: Custom system prompt for the LLM
        verbose: Enable verbose logging
    """
    # Configure logging
    if verbose:
        os.environ["LOG_LEVEL"] = "DEBUG"
    configure_logging()
    logger = get_logger(__name__)

    try:
        # Load environment from custom file if provided
        if env_file:
            if not env_file.exists():
                logger.error(f"Environment file not found: {env_file}")
                raise typer.Exit(1)
            from dotenv import load_dotenv

            load_dotenv(env_file)
            logger.info(f"Loaded custom environment from: {env_file}")

        # Override transport type if provided
        if transport_type:
            os.environ["TRANSPORT_TYPE"] = transport_type

        # Load and validate settings
        logger.info("Loading configuration...")
        settings = load_settings()

        # Display configuration
        logger.info("=" * 60)
        logger.info("Voice Agent Configuration")
        logger.info("=" * 60)
        logger.info(f"Transport: {settings.transport_type}")
        logger.info(f"LLM Model: {settings.llm_model}")
        logger.info(f"Sample Rate: {settings.audio_sample_rate} Hz")
        logger.info(f"TTS Optimization: Level {settings.tts_optimize_latency}")
        logger.info("=" * 60)

        # Initialize services
        logger.info("Initializing services...")

        transport = create_transport(settings)
        stt = create_stt_service(settings)
        llm, default_prompt = create_llm_service(settings)
        tts = create_tts_service(settings)

        # Use custom system prompt if provided
        final_system_prompt = system_prompt if system_prompt else default_prompt

        # Create LLM context with system prompt
        context = OpenAILLMContext(
            messages=[{"role": "system", "content": final_system_prompt}],
            tools=[],
        )
        context_aggregator = llm.create_context_aggregator(context)

        # Build pipeline
        logger.info("Building pipeline...")
        pipeline = Pipeline(
            [
                transport.input(),  # Audio input from transport
                stt,  # Speech to text
                context_aggregator.user(),  # Add user message to context
                llm,  # Generate response
                tts,  # Text to speech
                transport.output(),  # Audio output to transport
                context_aggregator.assistant(),  # Add assistant response to context
            ]
        )

        # Create pipeline task
        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                allow_interruptions=True,  # Enable interruption handling
                enable_metrics=True,  # Enable performance metrics
                enable_usage_metrics=True,  # Enable usage tracking
            ),
        )

        # Display ready message
        logger.success("=" * 60)
        logger.success("🎤 Voice agent is ready!")
        logger.success("Start speaking to interact with the AI assistant.")
        logger.success("Press Ctrl+C to stop.")
        logger.success("=" * 60)

        # Create and run the pipeline runner
        runner = PipelineRunner()
        await runner.run(task)

    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        logger.warning("Please check your .env file and ensure all required API keys are set.")
        logger.info("See .env.example for reference.")
        raise typer.Exit(1)

    except KeyboardInterrupt:
        logger.warning("\nShutting down voice agent...")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1)

    finally:
        logger.info("Voice agent stopped.")


@app.command()
def start(
    transport: str | None = typer.Option(
        None,
        "--transport",
        "-t",
        help="Transport type: 'websocket' (dev) or 'daily' (production)",
        show_default="from .env",
    ),
    env_file: Path | None = typer.Option(
        None,
        "--env-file",
        "-e",
        help="Path to custom .env file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    system_prompt: str | None = typer.Option(
        None,
        "--system-prompt",
        "-s",
        help="Custom system prompt for the LLM",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose/debug logging",
    ),
):
    """
    Start the voice agent with the specified configuration.

    The agent uses:
    • Cartesia Ink-Whisper for speech recognition (fastest TTCT)
    • Cerebras Llama 3.3-70B for language understanding (450 tok/sec)
    • ElevenLabs Flash v2.5 for speech synthesis (75ms latency)
    • Configurable WebSocket or Daily WebRTC transport

    Examples:
        # Start with WebSocket transport (default)
        voice-agent start

        # Start with Daily WebRTC transport
        voice-agent start --transport daily

        # Use custom .env file
        voice-agent start --env-file .env.production

        # Enable verbose logging
        voice-agent start --verbose
    """
    asyncio.run(
        run_voice_agent(
            transport_type=transport,
            env_file=env_file,
            system_prompt=system_prompt,
            verbose=verbose,
        )
    )


@app.command()
def version():
    """Show version information."""
    # Configure logging for this command
    configure_logging()
    logger = get_logger(__name__)

    logger.info(f"Voice Agent Platform version {__version__}")
    logger.info("")
    logger.info("Components:")
    logger.info("  • STT: Cartesia Ink-Whisper")
    logger.info("  • LLM: Cerebras Llama 3.3-70B")
    logger.info("  • TTS: ElevenLabs Flash v2.5")
    logger.info("  • Framework: Pipecat")


@app.command()
def config_check(
    env_file: Path | None = typer.Option(
        None,
        "--env-file",
        "-e",
        help="Path to custom .env file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
):
    """
    Validate configuration and check API keys.

    This command loads your configuration and validates all settings
    without starting the voice agent.
    """
    # Configure logging for this command
    configure_logging()
    logger = get_logger(__name__)

    try:
        # Load environment from custom file if provided
        if env_file:
            if not env_file.exists():
                logger.error(f"Environment file not found: {env_file}")
                raise typer.Exit(1)
            from dotenv import load_dotenv

            load_dotenv(env_file)

        # Load and validate settings
        settings = load_settings()

        logger.success("✓ Configuration is valid!")
        logger.info("")
        logger.info("Settings:")
        logger.info(f"  Transport Type: {settings.transport_type}")
        logger.info(f"  LLM Model: {settings.llm_model}")
        logger.info(f"  LLM Temperature: {settings.llm_temperature}")
        logger.info(f"  LLM Max Tokens: {settings.llm_max_tokens}")
        logger.info(f"  Audio Sample Rate: {settings.audio_sample_rate} Hz")
        logger.info(f"  TTS Optimization: Level {settings.tts_optimize_latency}")
        logger.info(f"  ElevenLabs Voice: {settings.elevenlabs_voice_id}")

        logger.info("")
        logger.info("API Keys:")
        logger.info(f"  Cartesia: {'✓ Set' if settings.cartesia_api_key else '✗ Missing'}")
        logger.info(f"  Cerebras: {'✓ Set' if settings.cerebras_api_key else '✗ Missing'}")
        logger.info(f"  ElevenLabs: {'✓ Set' if settings.elevenlabs_api_key else '✗ Missing'}")

        if settings.transport_type == "daily":
            logger.info(f"  Daily API Key: {'✓ Set' if settings.daily_api_key else '✗ Missing'}")
            logger.info(f"  Daily Room URL: {'✓ Set' if settings.daily_room_url else '✗ Missing'}")
            logger.info(f"  Daily Token: {'✓ Set' if settings.daily_token else '✗ Missing'}")

    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        logger.warning("Please check your .env file and ensure all required API keys are set.")
        logger.info("See .env.example for reference.")
        raise typer.Exit(1)


def cli():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    cli()
