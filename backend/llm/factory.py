from __future__ import annotations

from backend.llm.anthropic_llm import AnthropicLLM
from backend.llm.base import BaseLLM
from backend.llm.gemini_llm import GeminiLLM
from backend.llm.openai_llm import OpenAILLM


def get_llm(provider: str, config) -> BaseLLM:
    normalized_provider = provider.strip().lower()

    if normalized_provider == "anthropic":
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured")
        return AnthropicLLM(api_key=config.anthropic_api_key)
    if normalized_provider == "openai":
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        return OpenAILLM(api_key=config.openai_api_key)
    if normalized_provider == "gemini":
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
        return GeminiLLM(api_key=config.gemini_api_key)

    raise ValueError(f"Unsupported LLM provider: {provider}")
