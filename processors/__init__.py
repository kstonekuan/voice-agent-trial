"""Custom frame processors for voice dictation."""

from processors.llm_cleanup import LLMCleanupProcessor
from processors.text_inserter import TextInserterProcessor

__all__ = ["LLMCleanupProcessor", "TextInserterProcessor"]
