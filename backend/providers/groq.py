from __future__ import annotations

import json
import time

from groq import AsyncGroq

from backend.core.config import settings
from backend.schemas.llm import (
    LLMRequest,
    LLMResponse,
    LLMToolCall,
)


class GroqProvider:
    provider_name = "groq"

    def __init__(self) -> None:
        self.client = AsyncGroq(
            api_key=settings.groq_api_key,
        )

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        start_time = time.perf_counter()

        messages = []

        for message in request.messages:

            data = {
                "role": message.role,
                "content": message.content,
            }

            # Assistant tool calls
            if message.tool_calls:

                data["tool_calls"] = message.tool_calls

            # Tool response
            if message.tool_call_id:

                data["tool_call_id"] = message.tool_call_id

            messages.append(data)

        payload = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "max_tokens": request.max_tokens,
        }

        # ------------------------------------------------
        # Tool calling
        # ------------------------------------------------

        if request.tools:

            payload["tools"] = [
                tool.model_dump()
                for tool in request.tools
            ]

            payload["tool_choice"] = "auto"

        # ------------------------------------------------
        # Response format
        # ------------------------------------------------

        if request.response_format == "json":

            payload["response_format"] = {
                "type": "json_object",
            }

        try:

            response = await self.client.chat.completions.create(
                **payload,
            )

        except Exception as exc:

            raise RuntimeError(
                f"Groq request failed: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        execution_time_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        choice = response.choices[0]
        message = choice.message

        content = message.content or ""

        # ------------------------------------------------
        # Parse tool calls
        # ------------------------------------------------

        tool_calls: list[LLMToolCall] = []

        if message.tool_calls:

            for tool_call in message.tool_calls:

                function = tool_call.function

                arguments = function.arguments

                if isinstance(arguments, str):

                    try:
                        arguments = json.loads(arguments)

                    except json.JSONDecodeError:
                        arguments = {}

                if not isinstance(arguments, dict):
                    arguments = {}

                tool_calls.append(
                    LLMToolCall(
                        name=function.name,
                        arguments=arguments,
                        tool_call_id=tool_call.id,
                    )
                )

        # ------------------------------------------------
        # Token usage
        # ------------------------------------------------

        usage = getattr(response, "usage", None)

        prompt_tokens = None
        completion_tokens = None
        total_tokens = None

        if usage:

            prompt_tokens = getattr(
                usage,
                "prompt_tokens",
                None,
            )

            completion_tokens = getattr(
                usage,
                "completion_tokens",
                None,
            )

            total_tokens = getattr(
                usage,
                "total_tokens",
                None,
            )

        return LLMResponse(
            content=content,
            model=response.model,
            provider=self.provider_name,
            execution_time_ms=execution_time_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            response_format=request.response_format,
            tool_calls=tool_calls,
            raw_response=response.model_dump(),
        )
