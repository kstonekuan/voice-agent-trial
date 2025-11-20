"""Auto-formatter processor for cleaning and formatting transcribed text."""

import re
from typing import Any

from pipecat.frames.frames import Frame, TextFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from utils.logger import logger


class AutoFormatterProcessor(FrameProcessor):
    """Processor that auto-formats transcribed text.

    Features:
    - Removes filler words (um, uh, like, you know, etc.)
    - Adds punctuation (periods, commas)
    - Capitalizes sentences
    - Cleans up extra whitespace
    """

    # Common filler words to remove
    FILLER_WORDS = {
        "um",
        "uh",
        "uhm",
        "umm",
        "ah",
        "er",
        "hmm",
        "hm",
        "like",
        "you know",
        "i mean",
        "sort of",
        "kind of",
        "basically",
        "actually",
        "literally",
    }

    def __init__(self, enabled: bool = True, **kwargs: Any) -> None:
        """Initialize auto-formatter.

        Args:
            enabled: Whether auto-formatting is enabled
            **kwargs: Additional arguments for FrameProcessor
        """
        super().__init__(**kwargs)
        self._enabled = enabled

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Process incoming frames and format text frames.

        Args:
            frame: The frame to process
            direction: The direction of frame flow
        """
        await super().process_frame(frame, direction)

        # Only process TextFrames
        if not isinstance(frame, TextFrame):
            await self.push_frame(frame, direction)
            return

        # If disabled, pass through unchanged
        if not self._enabled:
            await self.push_frame(frame, direction)
            return

        # Format the text
        original_text = frame.text
        formatted_text = self._format_text(original_text)

        if formatted_text != original_text:
            logger.debug(f"Formatted: '{original_text}' -> '{formatted_text}'")

        # Create new frame with formatted text
        formatted_frame = TextFrame(text=formatted_text)
        await self.push_frame(formatted_frame, direction)

    def _format_text(self, text: str) -> str:
        """Format text with all transformations.

        Args:
            text: Raw transcribed text

        Returns:
            Formatted text
        """
        if not text or not text.strip():
            return text

        # Step 1: Remove filler words
        text = self._remove_filler_words(text)

        # Step 2: Clean up whitespace
        text = self._clean_whitespace(text)

        # Step 3: Add basic punctuation (if missing)
        text = self._add_punctuation(text)

        # Step 4: Capitalize sentences
        text = self._capitalize_sentences(text)

        return text.strip()

    def _remove_filler_words(self, text: str) -> str:
        """Remove common filler words.

        Args:
            text: Input text

        Returns:
            Text with filler words removed
        """
        # Create regex pattern for filler words (word boundaries)
        for filler in self.FILLER_WORDS:
            # Match filler word with word boundaries, case-insensitive
            pattern = r"\b" + re.escape(filler) + r"\b"
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        return text

    def _clean_whitespace(self, text: str) -> str:
        """Clean up extra whitespace.

        Args:
            text: Input text

        Returns:
            Text with normalized whitespace
        """
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)

        # Remove space before punctuation
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)

        # Add space after punctuation if missing
        text = re.sub(r"([.,!?;:])([A-Za-z])", r"\1 \2", text)

        return text.strip()

    def _add_punctuation(self, text: str) -> str:
        """Add basic punctuation if missing.

        Args:
            text: Input text

        Returns:
            Text with punctuation
        """
        if not text:
            return text

        # Add period at end if no punctuation exists
        if text[-1] not in ".!?":
            text += "."

        return text

    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize first letter of sentences.

        Args:
            text: Input text

        Returns:
            Text with capitalized sentences
        """
        # Split into sentences by punctuation
        sentences = re.split(r"([.!?]\s*)", text)

        # Capitalize first letter of each sentence
        result = []
        for part in sentences:
            if part and part[0].isalpha():
                result.append(part[0].upper() + part[1:])
            else:
                result.append(part)

        return "".join(result)
