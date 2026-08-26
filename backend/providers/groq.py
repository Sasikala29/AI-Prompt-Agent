"""
Groq LLM provider.
"""

import json
import time
from typing import Any

from groq import AsyncGroq

from backend.core.config import settings
from backend.providers.base import LLMProvider
from backend.schemas.llm import LLMRequest, LLMResponse, LLMToolCall


class GroqProvider(LLMProvider):

    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        self.client = AsyncGroq(
            api_key=settings.groq_api_key
        )

    @property
    def provider_name(self) -> str:
        return "groq"

    async def stream(
        self,
        request: LLMRequest,
    ):
        """
        Stream text chunks from Groq.
        """

        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.messages
        ]

        kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "max_tokens": request.max_tokens,
            "stream": True,
        }

        if request.tools:
            kwargs["tools"] = [
                tool.model_dump()
                for tool in request.tools
            ]

        try:
            stream = await self.client.chat.completions.create(
                **kwargs
            )

            async for chunk in stream:

                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                content = delta.content

                if isinstance(content, str) and content:
                    yield content

        except Exception as exc:
            raise RuntimeError(
                f"Groq streaming request failed: {exc}"
            ) from exc

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        started_at = time.perf_counter()

        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.messages
        ]

        kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "max_tokens": request.max_tokens,
        }

        if request.tools:
            kwargs["tools"] = [
                tool.model_dump()
                for tool in request.tools
            ]

        try:
            response = await self.client.chat.completions.create(
                **kwargs
            )

        except Exception as exc:
            raise RuntimeError(
                f"Groq request failed: {exc}"
            ) from exc

        execution_time_ms = (
            time.perf_counter() - started_at
        ) * 1000

        choice = response.choices[0]
        message = choice.message

        content = message.content or ""

        tool_calls: list[LLMToolCall] = []

        if message.tool_calls:
            for tool_call in message.tool_calls:

                function = tool_call.function
                arguments = function.arguments

                if isinstance(arguments, str):
                    try:
                        parsed_arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        parsed_arguments = {}
                elif isinstance(arguments, dict):
                    parsed_arguments = arguments
                else:
                    parsed_arguments = {}

                tool_calls.append(
                    LLMToolCall(
                        name=function.name,
                        arguments=parsed_arguments,
                    )
                )

        usage = response.usage

        return LLMResponse(
            model=response.model,
            content=content,
            provider=self.provider_name,
            execution_time_ms=round(
                execution_time_ms,
                2,
            ),
            prompt_tokens=(
                usage.prompt_tokens
                if usage
                else None
            ),
            completion_tokens=(
                usage.completion_tokens
                if usage
                else None
            ),
            total_tokens=(
                usage.total_tokens
                if usage
                else None
            ),
            response_format=request.response_format,
            tool_calls=tool_calls,
            raw_response=response.model_dump(),
        )
