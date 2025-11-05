#!/usr/bin/env python3
"""
Voice Agent Platform - Bot Implementation

A real-time voice assistant using:
- Cartesia Ink-Whisper (STT)
- Cerebras Llama 3.3-70B (LLM)
- ElevenLabs Flash v2.5 (TTS)
- Daily WebRTC (Transport)

This bot uses Pipecat's runner for automatic room/token management.
"""

import os
import sys
from pathlib import Path
from typing import Any

from loguru import logger
from PIL import Image
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    LLMRunFrame,
    OutputImageRawFrame,
    SpriteFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.runner.types import DailyRunnerArguments, RunnerArguments, SmallWebRTCRunnerArguments
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyTransport
from pipecat_tail.runner import TailRunner
from pydantic import ValidationError

from config.settings import Settings
from services.llm_service import create_llm_service
from services.stt_service import create_stt_service
from services.tts_service import create_tts_service

# Load animation sprites
sprites = []
script_dir = Path(__file__).parent

# Load sequential animation frames
for i in range(1, 26):
    # Build the full path to the image file
    full_path = script_dir / f"assets/robot0{i}.png"
    # Open the image and convert it to bytes
    with Image.open(full_path) as img:
        sprites.append(OutputImageRawFrame(image=img.tobytes(), size=img.size, format=img.format))

# Create a smooth animation by adding reversed frames
flipped = sprites[::-1]
sprites.extend(flipped)

# Define static and animated states
quiet_frame = sprites[0]  # Static frame for when bot is listening
talking_frame = SpriteFrame(images=sprites)  # Animation sequence for when bot is talking


class TalkingAnimation(FrameProcessor):
    """Manages the bot's visual animation states.

    Switches between static (listening) and animated (talking) states based on
    the bot's current speaking status.
    """

    def __init__(self) -> None:
        super().__init__()
        self._is_talking = False

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Process incoming frames and update animation state.

        Args:
            frame: The incoming frame to process
            direction: The direction of frame flow in the pipeline
        """
        await super().process_frame(frame, direction)

        # Switch to talking animation when bot starts speaking
        if isinstance(frame, BotStartedSpeakingFrame):
            if not self._is_talking:
                await self.push_frame(talking_frame)
                self._is_talking = True
        # Return to static frame when bot stops speaking
        elif isinstance(frame, BotStoppedSpeakingFrame):
            await self.push_frame(quiet_frame)
            self._is_talking = False

        await self.push_frame(frame, direction)


def configure_logger(verbose: bool = False) -> None:
    """
    Configure loguru logging with sensible defaults.

    Args:
        verbose: If True, set log level to DEBUG, otherwise use LOG_LEVEL env var
    """
    log_level_str = "DEBUG" if verbose else os.getenv("LOG_LEVEL", "INFO").upper()

    # Remove default handler
    logger.remove()

    # Add custom handler with colorization and formatting
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level_str,
        colorize=True,
    )


async def run_bot(transport: BaseTransport) -> None:
    """
    Main bot execution function.

    This follows the Pipecat example pattern.

    Args:
        transport: Configured Daily transport instance from runner
    """
    # Load configuration
    try:
        settings = Settings()
    except ValidationError as e:
        logger.error(f"Configuration Error: {e}")
        logger.warning("Please check your .env file and ensure all required API keys are set.")
        logger.info("See .env.example for reference.")
        return

    # Initialize services
    logger.info("Initializing services...")
    stt = create_stt_service(settings)
    llm = create_llm_service(settings)
    tts = create_tts_service(settings)

    # Create conversation messages
    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly AI assistant in a voice conversation. "
                "Your responses will be spoken aloud using text-to-speech. "
                "IMPORTANT: Never use tables, markdown formatting, bullet points, numbered lists, "
                "asterisks, emojis, special characters, or code blocks. "
                "Speak naturally as if having a verbal conversation. "
                "Use complete sentences and natural transitions instead of lists. "
                "Keep your answers conversational and concise."
            ),
        },
    ]

    # Set up conversation context
    context = LLMContext(messages)
    context_aggregator = LLMContextAggregatorPair(context)

    # RTVI events for Pipecat client UI
    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    # Create talking animation processor
    ta = TalkingAnimation()

    # Build pipeline
    logger.info("Building pipeline...")
    pipeline = Pipeline(
        [
            transport.input(),  # Audio input from transport
            stt,  # Speech to text
            rtvi,  # RTVI event handling
            context_aggregator.user(),  # Add user message to context
            llm,  # Generate response
            tts,  # Text to speech
            ta,  # Talking animation (after TTS)
            transport.output(),  # Audio output to transport
            context_aggregator.assistant(),  # Add assistant response to context
        ]
    )

    # Create pipeline task
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    # Queue the initial quiet frame
    await task.queue_frame(quiet_frame)

    # Register RTVI event handlers
    @rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi_processor: Any) -> None:  # noqa: ANN401
        logger.info("Client ready, setting bot ready")
        await rtvi_processor.set_bot_ready()
        # Kick off the conversation
        await task.queue_frames([LLMRunFrame()])

    # Register transport event handlers
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport_instance: Any, participant: Any) -> None:  # noqa: ANN401
        logger.success(f"✅ Client connected: {participant}")
        if isinstance(transport, DailyTransport):
            await transport.capture_participant_transcription(participant["id"])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport_instance: Any, client: Any) -> None:  # noqa: ANN401
        logger.info(f"Client disconnected: {client}")
        await task.cancel()

    # Display ready message
    logger.success("=" * 60)
    logger.success("🎤 Voice agent is ready!")
    logger.success("Waiting for client connection...")
    logger.success("=" * 60)

    # Run the pipeline
    runner = TailRunner(handle_sigint=False)
    await runner.run(task)


async def bot(runner_args: RunnerArguments) -> None:
    """
    Main bot entry point compatible with Pipecat runner.

    This function is called by the Pipecat runner for each new connection.

    Args:
        runner_args: Runner arguments provided by the Pipecat runner
    """
    logger.debug("runner args", runner_args)

    # Create VAD analyzer following Pipecat best practices
    vad_params = VADParams(
        stop_secs=0.2,  # Quick stop detection
    )
    vad = SileroVADAnalyzer(
        params=vad_params,
    )

    # Create turn analyzer for natural conversation flow
    turn_analyzer = LocalSmartTurnAnalyzerV3()

    transport = None

    if isinstance(runner_args, DailyRunnerArguments):
        logger.info(
            "Creating Daily transport",
            room_url=runner_args.room_url,
            has_token=bool(runner_args.token),
        )

        # Lazy import for Daily transport
        from pipecat.transports.daily.transport import DailyParams

        transport = DailyTransport(
            runner_args.room_url,
            runner_args.token,
            "Voice Agent",
            params=DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                video_out_enabled=True,
                video_out_width=1024,
                video_out_height=576,
                vad_analyzer=vad,
                turn_analyzer=turn_analyzer,
                transcription_enabled=True,
            ),
        )

    elif isinstance(runner_args, SmallWebRTCRunnerArguments):
        logger.info("Creating WebRTC transport")

        # Lazy import for WebRTC transport
        from pipecat.transports.network.small_webrtc import SmallWebRTCTransport

        transport = SmallWebRTCTransport(
            params=TransportParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                video_out_enabled=True,
                video_out_width=1024,
                video_out_height=576,
                video_out_is_live=True,
                vad_analyzer=vad,
                turn_analyzer=turn_analyzer,
            ),
            webrtc_connection=runner_args.webrtc_connection,
        )

    else:
        logger.error("This bot only supports Daily and webrtc transport")
        return

    # Run the bot
    await run_bot(transport)


if __name__ == "__main__":
    # Import and run the Pipecat runner
    from pipecat.runner.run import main

    main()
