"""LLM-based text cleanup processor for dictation."""

from typing import Any

from pipecat.frames.frames import Frame, TextFrame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.cerebras.llm import CerebrasLLMService

from utils.logger import logger

# System prompt for text cleanup
CLEANUP_SYSTEM_PROMPT = """You are a dictation cleanup assistant. Your task is to clean up transcribed speech.

Rules:
- Remove filler words (um, uh, like, you know, basically, actually, literally, sort of, kind of)
- Fix grammar and punctuation
- Capitalize sentences properly
- Keep the original meaning and tone intact
- Do NOT add any new information or change the intent
- Output ONLY the cleaned text, nothing else - no explanations, no quotes, no prefixes

Example:
Input: "um so basically I was like thinking we should uh you know update the readme file"
Output: I was thinking we should update the readme file."""


class LLMCleanupProcessor(FrameProcessor):
    """Processor that uses LLM to clean up transcribed text.

    This processor receives TranscriptionFrames from STT, sends them to
    an LLM for cleanup (removing filler words, fixing grammar), and
    outputs cleaned TextFrames.
    """

    def __init__(
        self,
        llm_service: CerebrasLLMService,
        **kwargs: Any,
    ) -> None:
        """Initialize LLM cleanup processor.

        Args:
            llm_service: Configured Cerebras LLM service for text cleanup
            **kwargs: Additional arguments for FrameProcessor
        """
        super().__init__(**kwargs)
        self._llm = llm_service

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Process incoming frames and clean up transcription text.

        Args:
            frame: The frame to process
            direction: The direction of frame flow
        """
        await super().process_frame(frame, direction)

        # Only process final TranscriptionFrames (not interim)
        if isinstance(frame, TranscriptionFrame):
            text = frame.text
            if text and text.strip():
                logger.debug(f"Cleaning transcription: {text[:50]}...")
                cleaned_text = await self._cleanup_text(text)
                logger.info(f"Cleaned: '{text}' -> '{cleaned_text}'")

                # Push cleaned text downstream
                cleaned_frame = TextFrame(text=cleaned_text)
                await self.push_frame(cleaned_frame, direction)
            return

        # Pass through all other frames unchanged
        await self.push_frame(frame, direction)

    async def _cleanup_text(self, text: str) -> str:
        """Clean up transcribed text using LLM.

        Args:
            text: Raw transcribed text

        Returns:
            Cleaned text
        """
        try:
            # Make a single-shot non-streaming call to the LLM
            response = await self._llm._client.chat.completions.create(
                model=self._llm.model_name,
                messages=[
                    {"role": "system", "content": CLEANUP_SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                stream=False,
                temperature=0.3,  # Lower temperature for more consistent cleanup
                max_tokens=500,
            )

            cleaned = response.choices[0].message.content
            if cleaned:
                return cleaned.strip()
            return text

        except Exception as e:
            logger.error(f"LLM cleanup failed: {e}")
            # Fall back to original text if cleanup fails
            return text
