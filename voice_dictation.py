#!/usr/bin/env python3
"""Voice Dictation Tool - CLI Application.

A local voice-to-text dictation tool using:
- Cartesia Ink-Whisper (STT)
- Local audio input (microphone)
- Auto-formatting (remove filler words, add punctuation)
- Direct text insertion (keyboard simulation)

Press and hold the hotkey to record, release to transcribe and type.
"""

import asyncio
import sys

import typer
from pynput import keyboard

from config.settings import Settings
from services.dictation_service import (
    create_dictation_pipeline,
    create_dictation_transport,
    run_dictation_pipeline,
)
from utils.logger import configure_logging, logger

# CLI app
app = typer.Typer(help="Voice dictation tool with push-to-talk")

# Global state
_is_recording = False
_transport: object | None = None


class DictationController:
    """Controls dictation state and handles keyboard events."""

    def __init__(self, hotkey_name: str = "ctrl_r") -> None:
        """Initialize dictation controller.

        Args:
            hotkey_name: Name of hotkey to use (ctrl_r, ctrl_l, alt_r, etc.)
        """
        self.hotkey_name = hotkey_name
        self.is_recording = False
        self.listener: keyboard.Listener | None = None
        self.transport: object | None = None

        # Map hotkey names to keyboard keys
        self.hotkey_map = {
            "ctrl_r": keyboard.Key.ctrl_r,
            "ctrl_l": keyboard.Key.ctrl_l,
            "alt_r": keyboard.Key.alt_r,
            "alt_l": keyboard.Key.alt_l,
            "shift_r": keyboard.Key.shift_r,
            "shift_l": keyboard.Key.shift_l,
        }

        self.hotkey = self.hotkey_map.get(hotkey_name, keyboard.Key.ctrl_r)

    def on_press(self, key: keyboard.Key) -> None:
        """Handle key press events.

        Args:
            key: The key that was pressed
        """
        if key == self.hotkey and not self.is_recording:
            self.is_recording = True
            logger.info("🎤 Recording started (hold to continue)...")
            # TODO: Start recording audio

    def on_release(self, key: keyboard.Key) -> None:
        """Handle key release events.

        Args:
            key: The key that was released
        """
        if key == self.hotkey and self.is_recording:
            self.is_recording = False
            logger.info("⌨️  Processing and typing...")
            # TODO: Stop recording and process

    def start_listening(self) -> None:
        """Start listening for keyboard events."""
        logger.info(f"Starting keyboard listener (hotkey: {self.hotkey_name})")
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def stop_listening(self) -> None:
        """Stop listening for keyboard events."""
        if self.listener:
            self.listener.stop()
            logger.info("Keyboard listener stopped")


def print_welcome(hotkey: str) -> None:
    """Print welcome message with instructions.

    Args:
        hotkey: The hotkey being used
    """
    logger.info("=" * 60)
    logger.success("🎤 Voice Dictation Tool Ready!")
    logger.info("=" * 60)
    logger.info(f"Hotkey: {hotkey.upper()}")
    logger.info("Usage:")
    logger.info("  1. Click into any text field")
    logger.info(f"  2. Press and HOLD {hotkey.upper()} to record")
    logger.info(f"  3. Release {hotkey.upper()} to transcribe and type")
    logger.info("  4. Move mouse to top-left corner to emergency stop")
    logger.info("")
    logger.info("Press Ctrl+C to quit")
    logger.info("=" * 60)


@app.command()
def main(
    hotkey: str = typer.Option(
        "ctrl_r",
        "--hotkey",
        "-k",
        help="Hotkey to trigger recording (ctrl_r, ctrl_l, alt_r, alt_l, shift_r, shift_l)",
    ),
    no_format: bool = typer.Option(
        False,
        "--no-format",
        help="Disable auto-formatting (keep filler words, no punctuation)",
    ),
    typing_speed: float = typer.Option(
        0.0,
        "--typing-speed",
        "-s",
        help="Delay between characters in seconds (0 = instant)",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Start the voice dictation tool.

    Examples:
        voice-dictation
        voice-dictation --hotkey alt_r
        voice-dictation --no-format --verbose
    """
    # Configure logging
    configure_logging()

    if verbose:
        logger.info("Verbose logging enabled")

    # Load settings
    try:
        settings = Settings()

        # Override settings with CLI options
        if no_format:
            settings.dictation_auto_format = False
            logger.info("Auto-formatting disabled")

        if typing_speed > 0:
            settings.dictation_typing_speed = typing_speed
            logger.info(f"Typing speed set to {typing_speed}s per character")

        # Override hotkey setting
        settings.dictation_hotkey = hotkey

    except Exception as e:
        logger.error(f"Configuration error: {e}")
        logger.warning("Please check your .env file and ensure all required API keys are set.")
        logger.info("See .env.example for reference.")
        sys.exit(1)

    # Print welcome message
    print_welcome(hotkey)

    # Create dictation controller
    controller = DictationController(hotkey_name=hotkey)

    # Start keyboard listener
    controller.start_listening()

    # Run dictation pipeline
    try:
        # Create transport and pipeline
        transport = create_dictation_transport(settings)
        pipeline = create_dictation_pipeline(settings, transport)
        controller.transport = transport

        # Run the pipeline
        asyncio.run(run_dictation_pipeline(settings, transport, pipeline))

    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down dictation tool...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        controller.stop_listening()
        logger.success("✓ Dictation tool stopped")


if __name__ == "__main__":
    app()
