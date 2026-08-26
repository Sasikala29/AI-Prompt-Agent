"""
Ollama LLM provider.
"""

import time
from typing import Any

import httpx

from backend.core.config import settings
from backend.providers.base import LLMProvider
from backend.schemas.llm import LLMRequest, LLMResponse, LLMToolCall


class OllamaProvider(LLMProvider):

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = (
            base_url or settings.ollama_base_url
        ).rstrip("/")

        self.timeout = timeout

    @property
    def provider_name(self) -> str:
        return "ollama"

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        url = f"{self.base_url}/api/chat"

        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.messages
        ]

        options: dict[str, Any] = {
            "temperature": request.temperature,
            "top_p": request.top_p,
            "num_predict": request.max_tokens,
        }

        payload: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "stream": request.stream,
            "options": options,
        }

        if request.response_format == "json":
            payload["format"] = "json"

        if request.tools:
            payload["tools"] = [
                tool.model_dump()
                for tool in request.tools
            ]

        started_at = time.perf_counter()

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                response = await client.post(
                    url,
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()

        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Unable to connect to Ollama. "
                f"Make sure Ollama is running on {self.base_url}."
            ) from exc

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "The Ollama request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            if status_code == 404:
                raise RuntimeError(
                    f"Ollama model '{request.model}' was not found. "
                    "Verify the installed model using 'ollama list'."
                ) from exc

            raise RuntimeError(
                f"Ollama returned HTTP {status_code}."
            ) from exc

        except ValueError as exc:
            raise RuntimeError(
                "Ollama returned an invalid JSON response."
            ) from exc

        except httpx.HTTPError as exc:
            raise RuntimeError(
                "An HTTP error occurred while communicating with Ollama."
            ) from exc

        execution_time_ms = (
            time.perf_counter() - started_at
        ) * 1000

        message_data = data.get(
            "message",
            {},
        )

        content = message_data.get(
            "content",
            "",
        )

        if not isinstance(content, str):
            raise RuntimeError(
                "Ollama returned an unexpected response format."
            )

        tool_calls: list[LLMToolCall] = []

        for tool_call in message_data.get(
            "tool_calls",
            [],
        ):
            function_data = tool_call.get(
                "function",
                {},
            )

            name = function_data.get(
                "name",
            )

            arguments = function_data.get(
                "arguments",
                {},
            )

            if name:
                tool_calls.append(
                    LLMToolCall(
                        name=name,
                        arguments=arguments
                        if isinstance(arguments, dict)
                        else {},
                    )
                )

        usage = self._extract_usage(data)

        return LLMResponse(
            model=data.get(
                "model",
                request.model,
            ),
            content=content,
            provider=self.provider_name,
            execution_time_ms=round(
                execution_time_ms,
                2,
            ),
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            total_tokens=usage["total_tokens"],
            response_format=request.response_format,
            tool_calls=tool_calls,
            raw_response=data,
        )

    async def stream(
        self,
        request: LLMRequest,
    ):
        """
        Stream text chunks from Ollama.
        """

        url = f"{self.base_url}/api/chat"

        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.messages
        ]

        options: dict[str, Any] = {
            "temperature": request.temperature,
            "top_p": request.top_p,
            "num_predict": request.max_tokens,
        }

        payload: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "stream": True,
            "options": options,
        }

        if request.response_format == "json":
            payload["format"] = "json"

        if request.tools:
            payload["tools"] = [
                tool.model_dump()
                for tool in request.tools
            ]

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                async with client.stream(
                    "POST",
                    url,
                    json=payload,
                ) as response:

                    response.raise_for_status()

                    async for line in response.aiter_lines():

                        if not line:
                            continue

                        try:
                            data = __import__("json").loads(line)
                        except ValueError:
                            continue

                        message = data.get(
                            "message",
                            {},
                        )

                        content = message.get(
                            "content",
                            "",
                        )

                        if isinstance(content, str) and content:
                            yield content

                        if data.get("done"):
                            break

        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Unable to connect to Ollama. "
                f"Make sure Ollama is running on {self.base_url}."
            ) from exc

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "The Ollama streaming request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            if status_code == 404:
                raise RuntimeError(
                    f"Ollama model '{request.model}' was not found. "
                    "Verify the installed model using 'ollama list'."
                ) from exc

            raise RuntimeError(
                f"Ollama returned HTTP {status_code}."
            ) from exc

        except httpx.HTTPError as exc:
            raise RuntimeError(
                "An HTTP error occurred while streaming from Ollama."
            ) from exc

    @staticmethod
    def _extract_usage(
        data: dict[str, Any],
    ) -> dict[str, int | None]:

        prompt_tokens = data.get(
            "prompt_eval_count"
        )

        completion_tokens = data.get(
            "eval_count"
        )

        total_tokens: int | None = None

        if (
            isinstance(prompt_tokens, int)
            and isinstance(completion_tokens, int)
        ):
            total_tokens = (
                prompt_tokens
                + completion_tokens
            )

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }
