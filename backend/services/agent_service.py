from __future__ import annotations

import json

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

            # ------------------------------------------------
            # No tool call -> final answer
            # ------------------------------------------------

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

            # ------------------------------------------------
            # IMPORTANT:
            # Preserve assistant tool_calls exactly in the
            # format required by Groq/OpenAI-compatible APIs.
            # ------------------------------------------------

            assistant_tool_calls = []

            for tool_call in response.tool_calls:

                assistant_tool_calls.append(
                    {
                        "id": tool_call.tool_call_id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": json.dumps(
                                tool_call.arguments,
                                ensure_ascii=False,
                            ),
                        },
                    }
                )

            messages.append(
                LLMMessage(
                    role="assistant",
                    content=response.content or "",
                    tool_calls=assistant_tool_calls,
                )
            )

            # ------------------------------------------------
            # Execute tools and append matching tool messages
            # ------------------------------------------------

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
                        content=result,
                        tool_call_id=tool_call.tool_call_id,
                    )
                )

        raise RuntimeError(
            "Agent exceeded the maximum number of tool-calling rounds."
        )

    @staticmethod
    def _ensure_json_response(content: str) -> str:
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
