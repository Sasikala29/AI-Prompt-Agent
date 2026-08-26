from __future__ import annotations

from backend.schemas.agent import StructuredAgentResponse
from backend.schemas.llm import (
    LLMMessage,
    LLMRequest,
    LLMTool,
)
from backend.services.agent_tools import AgentTools
from backend.services.llm_service import LLMService


class AgentService:
    """
    Agent orchestrator using native LLM tool calling.

    Model parameters are received from the UI and passed
    through to the LLM provider.
    """

    MAX_TOOL_ROUNDS = 3

    def __init__(
        self,
        llm_service: LLMService | None = None,
    ) -> None:
        self.llm_service = llm_service or LLMService()
        self.tools = AgentTools(
            llm_service=self.llm_service,
        )

    async def run(
        self,
        message: str,
        model: str = "mistral",
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 512,
        response_format: str = "text",
    ) -> StructuredAgentResponse:

        messages: list[LLMMessage] = [
            LLMMessage(
                role="system",
                content=(
                    "You are an AI Prompt Engineering Agent. "
                    "Use the available tools when appropriate. "
                    "If the user wants a new prompt, use "
                    "prompt_generation. "
                    "If the user provides an existing prompt to improve, "
                    "use prompt_improvement. "
                    "For normal questions, use general_llm. "
                    "After receiving a tool result, provide the final answer."
                ),
            ),
            LLMMessage(
                role="user",
                content=message.strip(),
            ),
        ]

        tools = [
            LLMTool(function=definition["function"])
            for definition in self.tools.definitions()
        ]

        detected_intent = "general"

        for round_number in range(self.MAX_TOOL_ROUNDS):

            # Tool-calling request should remain text-based.
            # JSON formatting is applied to the final response.
            request_format = (
                "text"
                if tools and round_number < self.MAX_TOOL_ROUNDS - 1
                else response_format
            )

            request = LLMRequest(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                response_format=request_format,
                stream=False,
                tools=tools,
            )

            response = await self.llm_service.generate(request)

            if not response.tool_calls:
                final_content = response.content.strip()

                if response_format == "json":
                    final_content = self._ensure_json_response(
                        final_content
                    )

                return StructuredAgentResponse(
                    intent=detected_intent,
                    response=final_content,
                    model=response.model,
                )

            messages.append(
                LLMMessage(
                    role="assistant",
                    content=response.content,
                )
            )

            for tool_call in response.tool_calls:

                detected_intent = tool_call.name

                result = await self.tools.execute(
                    name=tool_call.name,
                    arguments=tool_call.arguments,
                    model=model,
                )

                messages.append(
                    LLMMessage(
                        role="tool",
                        content=(
                            f"Tool: {tool_call.name}\n"
                            f"Result: {result}"
                        ),
                    )
                )

        raise RuntimeError(
            "Agent exceeded the maximum number of tool-calling rounds."
        )

    @staticmethod
    def _ensure_json_response(content: str) -> str:
        """
        Ensure JSON mode returns valid JSON text.

        Ollama normally guarantees JSON when format=json,
        but this fallback prevents malformed output from
        breaking the frontend.
        """

        import json

        try:
            parsed = json.loads(content)

            if isinstance(parsed, dict):
                return json.dumps(
                    parsed,
                    indent=2,
                    ensure_ascii=False,
                )

            return json.dumps(
                {"response": parsed},
                indent=2,
                ensure_ascii=False,
            )

        except (json.JSONDecodeError, TypeError):
            return json.dumps(
                {"response": content},
                indent=2,
                ensure_ascii=False,
            )
