"""
Provider abstraction for LLM integrations.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from backend.schemas.llm import LLMRequest, LLMResponse


class LLMProvider(ABC):

    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        raise NotImplementedError

    @abstractmethod
    async def stream(
        self,
        request: LLMRequest,
    ) -> AsyncIterator[str]:
        raise NotImplementedError
