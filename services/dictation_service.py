"""Dictation service initialization and pipeline setup."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

from config.settings import Settings
from processors.llm_cleanup import LLMCleanupProcessor
from processors.text_inserter import TextInserterProcessor
from services.llm_service import create_llm_service
from services.stt_service import create_stt_service
from utils.logger import logger

if TYPE_CHECKING:
    from voice_dictation import DictationController


def create_dictation_transport(settings: Settings) -> LocalAudioTransport:
    """Create local audio transport for dictation.

    Args:
        settings: Application settings

    Returns:
        Configured LocalAudioTransport instance
    """
    logger.info("Initializing local audio transport for dictation")

    return LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=True,
            audio_out_enabled=False,  # No audio output for dictation
            vad_analyzer=SileroVADAnalyzer(),
        )
    )


def create_dictation_pipeline(
    settings: Settings,
    transport: LocalAudioTransport,
) -> Pipeline:
    """Create the dictation processing pipeline.

    Pipeline flow:
    1. LocalAudioTransport (microphone input)
    2. CartesiaSTTService (speech-to-text)
    3. LLMCleanupProcessor (Cerebras text cleanup)
    4. TextInserterProcessor (keyboard simulation)

    Args:
        settings: Application settings
        transport: Local audio transport

    Returns:
        Configured Pipeline instance
    """
    logger.info("Building dictation pipeline")

    # Initialize services
    stt_service = create_stt_service(settings)
    llm_service = create_llm_service(settings)

    # Initialize processors
    llm_cleanup = LLMCleanupProcessor(llm_service=llm_service)

    text_inserter = TextInserterProcessor(
        typing_speed=settings.dictation_typing_speed,
        pre_typing_delay=0.1,
    )

    # Build pipeline
    pipeline = Pipeline(
        [
            transport.input(),  # Microphone input with VAD
            stt_service,  # Speech-to-text transcription
            llm_cleanup,  # LLM-based text cleanup
            text_inserter,  # Type into active window
        ]
    )

    logger.info("Dictation pipeline built successfully")
    return pipeline


async def _wait_for_stream_and_pause(
    transport: LocalAudioTransport,
    controller: DictationController,
    timeout: float = 10.0,
) -> None:
    """Wait for audio stream to be initialized, then pause it.

    Args:
        transport: Local audio transport
        controller: Dictation controller to notify
        timeout: Maximum time to wait in seconds
    """
    elapsed = 0.0
    interval = 0.1

    while elapsed < timeout:
        # Check if the input transport and stream exist
        input_transport = getattr(transport, "_input", None)
        if input_transport:
            stream = getattr(input_transport, "_in_stream", None)
            if stream is not None:
                # Stream is ready - notify controller
                controller.mark_stream_ready()
                return

        await asyncio.sleep(interval)
        elapsed += interval

    logger.warning("Timeout waiting for audio stream to initialize")


async def run_dictation_pipeline(
    settings: Settings,
    transport: LocalAudioTransport,
    pipeline: Pipeline,
    controller: DictationController,
) -> None:
    """Run the dictation pipeline.

    Args:
        settings: Application settings
        transport: Local audio transport
        pipeline: Configured pipeline
        controller: Dictation controller for PTT control
    """
    logger.info("Starting dictation pipeline")

    # Create pipeline task
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=False,  # No interruptions in dictation mode
            enable_metrics=settings.dictation_show_preview,
            enable_usage_metrics=True,
        ),
    )

    # Run pipeline
    runner = PipelineRunner()

    try:
        # Start the stream initialization watcher as a background task
        stream_watcher = asyncio.create_task(_wait_for_stream_and_pause(transport, controller))

        # Run the pipeline (this blocks until pipeline ends)
        await runner.run(task)

        # Cancel stream watcher if still running
        stream_watcher.cancel()

    except KeyboardInterrupt:
        logger.info("Dictation interrupted by user")
    except Exception as e:
        logger.error(f"Dictation pipeline error: {e}")
        raise
    finally:
        logger.info("Dictation pipeline stopped")
