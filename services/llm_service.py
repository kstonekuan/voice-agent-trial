"""Cerebras LLM service initialization."""

from loguru import logger
from pipecat.services.cerebras.llm import CerebrasLLMService

from config.settings import Settings


def create_llm_service(
    settings: Settings,
) -> CerebrasLLMService:
    """
    Initialize Cerebras LLM service with voice-optimized settings.

    Args:
        settings: Application settings
        system_prompt: Optional custom system prompt (uses default if None)

    Returns:
        Configured CerebrasLLMService instance
    """

    logger.info(
        "initializing_cerebras_llm",
    )

    return CerebrasLLMService(
        api_key=settings.cerebras_api_key,
    )
