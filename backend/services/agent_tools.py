from __future__ import annotations

from backend.services.llm_service import LLMService


class AgentTools:

    def __init__(
        self,
        llm_service: LLMService | None = None,
    ) -> None:
        self.llm_service = llm_service or LLMService()

    def definitions(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "prompt_generation",
                    "description": "Create an optimized prompt from a user's requirement.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The user's requirement.",
                            }
                        },
                        "required": ["message"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "prompt_improvement",
                    "description": "Improve an existing prompt.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The existing prompt to improve.",
                            }
                        },
                        "required": ["message"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "general_llm",
                    "description": "Answer a normal user question directly.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The user's question.",
                            }
                        },
                        "required": ["message"],
                    },
                },
            },
        ]

    async def prompt_generation(
        self,
        message: str,
        model: str,
    ) -> str:
        return await self._generate(
            "Create a high-quality optimized prompt for this request:\n\n"
            + message,
            model,
        )

    async def prompt_improvement(
        self,
        message: str,
        model: str,
    ) -> str:
        return await self._generate(
            "Improve the following prompt while preserving its intent:\n\n"
            + message,
            model,
        )

    async def general_llm(
        self,
        message: str,
        model: str,
    ) -> str:
        return await self._generate(
            message,
            model,
        )

    async def execute(
        self,
        name: str,
        arguments: dict,
        model: str,
    ) -> str:

        if name == "prompt_generation":
            return await self.prompt_generation(
                arguments["message"],
                model,
            )

        if name == "prompt_improvement":
            return await self.prompt_improvement(
                arguments["message"],
                model,
            )

        if name == "general_llm":
            return await self.general_llm(
                arguments["message"],
                model,
            )

        return f"Unknown tool: {name}"

    async def _generate(
        self,
        message: str,
        model: str,
    ) -> str:

        from backend.schemas.llm import (
            LLMMessage,
            LLMRequest,
        )

        request = LLMRequest(
            model=model,
            messages=[
                LLMMessage(
                    role="user",
                    content=message,
                )
            ],
            temperature=0.4,
            top_p=0.9,
            max_tokens=512,
            response_format="text",
            stream=False,
        )

        response = await self.llm_service.generate(
            request
        )

        return response.content.strip()
