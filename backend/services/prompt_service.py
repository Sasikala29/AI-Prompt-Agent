"""
Business service for prompt generation.
"""

from backend.prompts.engine import (
    GeneratedPrompt,
    PromptEngine,
    PromptExample,
    PromptRequest,
)
from backend.schemas.prompts import PromptGenerateRequest


class PromptService:
    """
    Coordinates API input with the reusable PromptEngine.

    This service contains no HTTP-specific logic and no LLM calls.
    """

    def __init__(self, engine: PromptEngine | None = None):
        self.engine = engine or PromptEngine()

    def generate_prompt(
        self,
        request: PromptGenerateRequest,
    ) -> GeneratedPrompt:
        """Convert API input into a generated prompt."""

        engine_request = PromptRequest(
            task=request.task,
            technique=request.technique,
            role=request.role,
            examples=[
                PromptExample(
                    input=example.input,
                    output=example.output,
                )
                for example in request.examples
            ],
            context=request.context,
            constraints=request.constraints,
            expected_output=request.expected_output,
        )

        return self.engine.generate(engine_request)