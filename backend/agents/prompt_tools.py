from __future__ import annotations

from backend.agents.tools import AgentTool, ToolRegistry
from backend.services.llm_service import LLMService
from backend.schemas.llm import LLMMessage, LLMRequest


async def generate_prompt(
    request: str,
    model: str = "mistral",
) -> str:
    return await _generate(
        system_prompt=(
            "You are an expert prompt engineer. "
            "Create a clear, specific and optimized prompt "
            "for the user's requirement. Return only the "
            "optimized prompt."
        ),
        user_prompt=request,
        model=model,
    )


async def improve_prompt(
    prompt: str,
    model: str = "mistral",
) -> str:
    return await _generate(
        system_prompt=(
            "You are an expert prompt engineer. "
            "Improve the user's prompt for clarity, "
            "specificity, constraints and output quality. "
            "Return the improved prompt."
        ),
        user_prompt=prompt,
        model=model,
    )


async def compare_prompts(
    prompt_a: str,
    prompt_b: str,
    model: str = "mistral",
) -> str:
    user_prompt = f"""
Compare these two prompts.

PROMPT A:
{prompt_a}

PROMPT B:
{prompt_b}

Evaluate:
- Clarity
- Specificity
- Context
- Constraints
- Output requirements
- Expected response quality

Return:
1. Better prompt
2. Reason
3. Key improvements
""".strip()

    return await _generate(
        system_prompt=(
            "You are an expert prompt engineering evaluator. "
            "Compare prompts objectively and provide a concise "
            "useful evaluation."
        ),
        user_prompt=user_prompt,
        model=model,
    )


async def _generate(
    system_prompt: str,
    user_prompt: str,
    model: str,
) -> str:
    llm_service = LLMService()

    request = LLMRequest(
        model=model,
        messages=[
            LLMMessage(
                role="system",
                content=system_prompt,
            ),
            LLMMessage(
                role="user",
                content=user_prompt,
            ),
        ],
        temperature=0.4,
        top_p=0.9,
        max_tokens=512,
        response_format="text",
        stream=False,
    )

    response = await llm_service.generate(request)

    return response.content.strip()


def create_prompt_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        AgentTool(
            name="generate_prompt",
            description=(
                "Creates an optimized prompt from a user requirement."
            ),
            function=generate_prompt,
        )
    )

    registry.register(
        AgentTool(
            name="improve_prompt",
            description=(
                "Improves an existing prompt for clarity and quality."
            ),
            function=improve_prompt,
        )
    )

    registry.register(
        AgentTool(
            name="compare_prompts",
            description=(
                "Compares two prompts and determines which is better."
            ),
            function=compare_prompts,
        )
    )

    return registry