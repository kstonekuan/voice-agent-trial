"""Dictation service initialization and pipeline setup."""

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

from config.settings import Settings
from processors.auto_formatter import AutoFormatterProcessor
from processors.text_inserter import TextInserterProcessor
from services.stt_service import create_stt_service
from utils.logger import logger


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
    3. AutoFormatterProcessor (text cleanup)
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

    # Initialize processors
    auto_formatter = AutoFormatterProcessor(enabled=settings.dictation_auto_format)

    text_inserter = TextInserterProcessor(
        typing_speed=settings.dictation_typing_speed,
        pre_typing_delay=0.1,
    )

    # Build pipeline
    pipeline = Pipeline(
        [
            transport.input(),  # Microphone input with VAD
            stt_service,  # Speech-to-text transcription
            auto_formatter,  # Clean up and format text
            text_inserter,  # Type into active window
        ]
    )

    logger.info("Dictation pipeline built successfully")
    return pipeline


async def run_dictation_pipeline(
    settings: Settings,
    transport: LocalAudioTransport,
    pipeline: Pipeline,
) -> None:
    """Run the dictation pipeline.

    Args:
        settings: Application settings
        transport: Local audio transport
        pipeline: Configured pipeline
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
        await runner.run(task)
    except KeyboardInterrupt:
        logger.info("Dictation interrupted by user")
    except Exception as e:
        logger.error(f"Dictation pipeline error: {e}")
        raise
    finally:
        logger.info("Dictation pipeline stopped")
