from __future__ import annotations

from time import perf_counter

from backend.prompts.engine import (
    PromptEngine,
    PromptExample,
    PromptRequest,
)
from backend.schemas.comparison import (
    PromptComparisonRequest,
    PromptComparisonResponse,
    PromptComparisonResult,
)
from backend.schemas.llm import (
    LLMMessage,
    LLMRequest,
)
from backend.services.llm_service import LLMService


class PromptComparisonService:
    """
    Compares multiple prompt engineering techniques
    against the same task using the configured LLM.
    """

    def __init__(self) -> None:
        self.prompt_engine = PromptEngine()
        self.llm_service = LLMService()

    async def compare(
        self,
        request: PromptComparisonRequest,
    ) -> PromptComparisonResponse:

        results: list[PromptComparisonResult] = []

        examples = [
            PromptExample(
                input=example["input"],
                output=example["output"],
            )
            for example in request.examples
        ]

        for technique in request.techniques:

            prompt_request = PromptRequest(
                task=request.task,
                technique=technique,
                role=request.role,
                examples=examples,
                context=request.context,
                constraints=request.constraints,
                expected_output=request.expected_output,
            )

            generated_prompt = self.prompt_engine.generate(
                prompt_request
            )

            prompt = generated_prompt.prompt

            llm_request = LLMRequest(
                model=request.model,
                messages=[
                    LLMMessage(
                        role="user",
                        content=prompt,
                    )
                ],
                temperature=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens,
            )

            start_time = perf_counter()

            response = await self.llm_service.generate(
                llm_request
            )

            execution_time_ms = (
                perf_counter() - start_time
            ) * 1000

            results.append(
                PromptComparisonResult(
                    technique=technique,
                    prompt=prompt,
                    response=response.content,
                    model=response.model,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    max_tokens=request.max_tokens,
                    execution_time_ms=round(
                        execution_time_ms,
                        2,
                    ),
                    total_tokens=response.total_tokens,
                )
            )

        return PromptComparisonResponse(
            task=request.task,
            results=results,
        )