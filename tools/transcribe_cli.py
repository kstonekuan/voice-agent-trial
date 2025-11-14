#!/usr/bin/env python3
"""
CLI Transcription Tool

Captures audio from your computer and outputs live transcriptions to the CLI.
Uses Cartesia Ink-Whisper for speech-to-text.

For system audio capture (browser/videos), you need to configure audio loopback.
See docs/audio_loopback_setup.md for setup instructions.
"""

import asyncio
import sys
from datetime import datetime

from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (
    Frame,
    TranscriptionFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams
from pydantic import ValidationError

from config.settings import Settings
from services.stt_service import create_stt_service


class TranscriptionPrinter(FrameProcessor):
    """Prints transcriptions to stdout in real-time."""

    def __init__(self) -> None:
        super().__init__()
        self._print_header()

    def _print_header(self) -> None:
        """Print initial header."""
        print("=" * 80)
        print("🎤 Real-Time Transcription")
        print("=" * 80)
        print("Listening... (Press Ctrl+C to stop)")
        print("-" * 80)
        sys.stdout.flush()

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Process incoming frames and print transcriptions.

        Args:
            frame: The incoming frame to process
            direction: The direction of frame flow in the pipeline
        """
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            # Get timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Print transcription with timestamp
            print(f"[{timestamp}] {frame.text}")
            sys.stdout.flush()

        await self.push_frame(frame, direction)


async def run_transcription(device_index: int | None = None) -> None:
    """
    Run the transcription pipeline.

    Args:
        device_index: Optional audio device index to use
    """
    # Load configuration
    try:
        settings = Settings()
    except ValidationError as e:
        logger.error(f"Configuration Error: {e}")
        logger.warning("Please check your .env file and ensure all required API keys are set.")
        logger.info("See .env.example for reference.")
        return

    # Create VAD analyzer following voice_agent.py pattern
    logger.info("Initializing VAD analyzer...")
    vad_params = VADParams(
        stop_secs=0.2,  # Quick stop detection
    )
    vad = SileroVADAnalyzer(
        params=vad_params,
    )

    # Create transport for audio input only (no output)
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=True,
            audio_out_enabled=False,
            audio_in_sample_rate=16000,  # 16kHz for STT
            audio_in_channels=1,  # Mono audio
            vad_analyzer=vad,  # Add VAD to keep stream alive
            input_device_index=device_index,
        )
    )

    # Create STT service using existing configuration
    logger.info("Initializing Cartesia STT service...")
    stt = create_stt_service(settings)

    # Create transcription printer
    transcription_printer = TranscriptionPrinter()

    # Build minimal pipeline: Audio Input → STT → Print
    logger.info("Building transcription pipeline...")
    pipeline = Pipeline(
        [
            transport.input(),  # Audio input from microphone/loopback device
            stt,  # Speech to text
            transcription_printer,  # Print to CLI
        ]
    )

    # Create pipeline task with minimal params
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=False,
            enable_metrics=False,
            enable_usage_metrics=False,
        ),
    )

    # Run the pipeline
    runner = PipelineRunner(handle_sigint=True)
    await runner.run(task)


def list_audio_devices() -> None:
    """List all available audio input devices."""
    try:
        import pyaudio

        audio = pyaudio.PyAudio()

        print("\n" + "=" * 80)
        print("Available Audio Input Devices:")
        print("=" * 80)

        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            # Only show input devices
            if device_info["maxInputChannels"] > 0:
                print(f"\nDevice {i}: {device_info['name']}")
                print(f"  Channels: {device_info['maxInputChannels']}")
                print(f"  Sample Rate: {device_info['defaultSampleRate']} Hz")

        audio.terminate()
        print("\n" + "=" * 80)
        print("To use a specific device, run: uv run transcribe --device <index>")
        print("=" * 80 + "\n")

    except ImportError:
        logger.error("PyAudio not installed. Run: sudo apt-get install portaudio19-dev")
        logger.error("Then: uv sync")
    except Exception as e:
        logger.error(f"Error listing devices: {e}")


def main() -> None:
    """Main entry point for the CLI tool."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Real-time audio transcription CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run transcribe                    # Use default audio device
  uv run transcribe --device 2         # Use specific device
  uv run transcribe --list-devices     # List available devices

For system audio capture (browser/videos), see docs/audio_loopback_setup.md
        """,
    )

    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="Audio device index to use (see --list-devices)",
    )

    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List all available audio input devices and exit",
    )

    args = parser.parse_args()

    # Handle --list-devices flag
    if args.list_devices:
        list_audio_devices()
        return

    # Run transcription
    try:
        asyncio.run(run_transcription(device_index=args.device))
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("✅ Transcription stopped")
        print("=" * 80)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
