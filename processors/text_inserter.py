"""Text inserter processor for simulating keyboard typing."""

import asyncio
from typing import Any

import pyautogui
from pipecat.frames.frames import Frame, TextFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from utils.logger import logger


class TextInserterProcessor(FrameProcessor):
    """Processor that inserts text by simulating keyboard typing.

    This processor takes TextFrames and types them into the currently
    focused application using keyboard simulation.
    """

    def __init__(
        self,
        typing_speed: float = 0.0,
        pre_typing_delay: float = 0.1,
        **kwargs: Any,
    ) -> None:
        """Initialize text inserter.

        Args:
            typing_speed: Delay between characters (0 = instant)
            pre_typing_delay: Delay before starting to type (seconds)
            **kwargs: Additional arguments for FrameProcessor
        """
        super().__init__(**kwargs)
        self._typing_speed = typing_speed
        self._pre_typing_delay = pre_typing_delay

        # Configure pyautogui safety features
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = float(typing_speed)

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Process incoming frames and insert text frames.

        Args:
            frame: The frame to process
            direction: The direction of frame flow
        """
        await super().process_frame(frame, direction)

        # Only process TextFrames
        if not isinstance(frame, TextFrame):
            await self.push_frame(frame, direction)
            return

        text = frame.text
        if not text or not text.strip():
            await self.push_frame(frame, direction)
            return

        # Insert the text
        await self._insert_text(text)

        # Push frame downstream
        await self.push_frame(frame, direction)

    async def _insert_text(self, text: str) -> None:
        """Insert text by simulating keyboard typing.

        Args:
            text: Text to type
        """
        logger.info(f"Inserting text: {text[:50]}...")

        try:
            # Small delay to ensure the target window is focused
            if self._pre_typing_delay > 0:
                await asyncio.sleep(self._pre_typing_delay)

            # Run typing in thread pool to avoid blocking
            await asyncio.get_event_loop().run_in_executor(None, self._type_text_sync, text)

            logger.debug(f"Successfully inserted {len(text)} characters")

        except Exception as e:
            logger.error(f"Failed to insert text: {e}")

    def _type_text_sync(self, text: str) -> None:
        """Synchronously type text using pyautogui.

        Args:
            text: Text to type
        """
        if self._typing_speed == 0:
            # Instant typing
            pyautogui.write(text, interval=0)
        else:
            # Character-by-character with delay
            pyautogui.write(text, interval=self._typing_speed)
