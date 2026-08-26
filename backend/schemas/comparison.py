from pydantic import BaseModel, Field, field_validator

from backend.prompts.engine import PromptTechnique


class PromptComparisonRequest(BaseModel):
    """
    Request model for comparing multiple prompting techniques
    against the same user task.
    """

    task: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The task/question to send through different prompt techniques.",
    )

    techniques: list[PromptTechnique] = Field(
        ...,
        min_length=1,
        description="Prompting techniques to compare.",
    )

    role: str | None = Field(
        default=None,
        max_length=500,
        description="Role used by role-based prompting.",
    )

    examples: list[dict[str, str]] = Field(
        default_factory=list,
        description="Examples used by one-shot and few-shot prompting.",
    )

    context: str | None = Field(
        default=None,
        max_length=3000,
        description="Optional context for structured prompting.",
    )

    constraints: str | None = Field(
        default=None,
        max_length=3000,
        description="Optional constraints for structured prompting.",
    )

    expected_output: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional expected output format.",
    )

    model: str = Field(
        default="mistral",
        min_length=1,
        max_length=100,
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
    )

    top_p: float = Field(
        default=0.9,
        gt=0.0,
        le=1.0,
    )

    max_tokens: int = Field(
        default=512,
        ge=1,
        le=4096,
    )

    @field_validator("task")
    @classmethod
    def validate_task(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Task cannot be empty.")

        return value

    @field_validator("techniques")
    @classmethod
    def validate_techniques(
        cls,
        value: list[PromptTechnique],
    ) -> list[PromptTechnique]:
        if not value:
            raise ValueError("At least one prompting technique is required.")

        # Remove duplicates while preserving the user's selection order.
        return list(dict.fromkeys(value))


class PromptComparisonResult(BaseModel):
    """
    Result for one prompting technique.
    """

    technique: PromptTechnique
    prompt: str
    response: str
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    execution_time_ms: float
    total_tokens: int | None = None


class PromptComparisonResponse(BaseModel):
    """
    Complete response returned by the comparison service.
    """

    task: str
    results: list[PromptComparisonResult]