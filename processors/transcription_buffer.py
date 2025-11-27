"""Transcription buffer processor for dictation.

Buffers transcription text until the user stops speaking (VAD signals end of utterance),
then emits a single consolidated transcription for LLM cleanup.
"""

from datetime import datetime, timezone
from typing import Any

from pipecat.frames.frames import Frame, TranscriptionFrame, UserStoppedSpeakingFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from utils.logger import logger


class TranscriptionBufferProcessor(FrameProcessor):
    """Buffers transcriptions until user stops speaking.

    This processor accumulates transcription text from partial STT results
    and emits a single consolidated TranscriptionFrame when the VAD detects
    the user has stopped speaking. This allows the LLM cleanup to process
    complete utterances instead of fragments.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the transcription buffer processor."""
        super().__init__(**kwargs)
        self._buffer: str = ""
        self._last_user_id: str = "user"
        self._last_language = None

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Process frames, buffering transcriptions until end of speech.

        Args:
            frame: The frame to process
            direction: The direction of frame flow
        """
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            # Accumulate transcription text and save metadata
            text = frame.text
            if text:
                self._buffer += text
                self._last_user_id = frame.user_id
                self._last_language = frame.language
                logger.debug(f"Buffered transcription: '{text}' (total: '{self._buffer}')")
            # Don't push TranscriptionFrame - we'll emit consolidated version later
            return

        if isinstance(frame, UserStoppedSpeakingFrame):
            # User stopped speaking - flush the buffer
            if self._buffer.strip():
                logger.info(f"Flushing transcription buffer: '{self._buffer.strip()}'")
                timestamp = datetime.now(timezone.utc).isoformat()
                consolidated_frame = TranscriptionFrame(
                    text=self._buffer.strip(),
                    user_id=self._last_user_id,
                    timestamp=timestamp,
                    language=self._last_language,
                )
                await self.push_frame(consolidated_frame, direction)
                self._buffer = ""
            # Pass through the UserStoppedSpeakingFrame
            await self.push_frame(frame, direction)
            return

        # Pass through all other frames unchanged
        await self.push_frame(frame, direction)
