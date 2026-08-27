from __future__ import annotations

from collections.abc import AsyncIterator

from backend.core.config import settings
from backend.providers.base import LLMProvider
from backend.providers.groq import GroqProvider
from backend.providers.ollama import OllamaProvider
from backend.schemas.llm import LLMRequest, LLMResponse


class LLMService:
    """
    Application-level LLM service.

    Routes requests to the correct provider based on model name.
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
    ) -> None:
        self.provider = provider

        self.ollama = OllamaProvider()
        self.groq = GroqProvider()

    def _get_provider(
        self,
        model: str,
    ) -> LLMProvider:

        model_name = model.strip().lower()

        if model_name == settings.groq_model.lower():
            return self.groq

        if model_name == settings.ollama_model.lower():
            return self.ollama

        raise ValueError(
            f"Unsupported LLM model '{model}'. "
            f"Supported models: "
            f"{settings.groq_model}, "
            f"{settings.ollama_model}"
        )

    def get_provider(
        self,
        model: str,
    ) -> LLMProvider:

        return self.provider or self._get_provider(model)

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        provider = self.get_provider(request.model)

        return await provider.generate(request)

    async def stream(
        self,
        request: LLMRequest,
    ) -> AsyncIterator[str]:

        provider = self.get_provider(request.model)

        async for chunk in provider.stream(request):
            yield chunk