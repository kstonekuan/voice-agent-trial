"""Cerebras LLM service initialization."""

from pipecat.services.cerebras.llm import CerebrasLLMService

from config.settings import Settings

DEFAULT_SYSTEM_PROMPT = """You are a helpful personal AI assistant engaging in voice conversation.

Guidelines for voice interaction:
- Respond conversationally and naturally as if speaking to someone
- Keep responses brief and concise (typically 1-3 sentences)
- For complex topics, provide a summary and offer to elaborate if needed
- Use spoken language, not written formatting (say "twenty twenty-five" not "2025")
- Avoid bullet points, numbered lists, or markdown - these don't work well in speech
- If uncertain, acknowledge it clearly and concisely
- Respond directly to what the user asked without unnecessary preamble

Your goal is natural, helpful conversation optimized for voice interaction."""


def create_llm_service(
    settings: Settings,
    system_prompt: str | None = None,
) -> tuple[CerebrasLLMService, str]:
    """
    Initialize Cerebras LLM service with voice-optimized settings.

    Args:
        settings: Application settings
        system_prompt: Optional custom system prompt (uses default if None)

    Returns:
        Configured CerebrasLLMService instance
    """
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    llm = CerebrasLLMService(
        api_key=settings.cerebras_api_key,
        model=settings.llm_model,
    )

    return llm, system_prompt


def get_llm_params(settings: Settings) -> dict:
    """
    Get LLM generation parameters optimized for voice.

    Args:
        settings: Application settings

    Returns:
        Dictionary of LLM parameters
    """
    return {
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
        "top_p": 0.9,
        "frequency_penalty": 0.2,  # Reduce repetition
    }
