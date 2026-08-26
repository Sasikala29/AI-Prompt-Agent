"""
API schemas for prompt generation.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from backend.prompts.engine import PromptTechnique


class PromptExampleRequest(BaseModel):
    """Input/output example used by one-shot and few-shot prompting."""

    input: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    output: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    @field_validator("input", "output")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty.")

        return value


class PromptGenerateRequest(BaseModel):
    """Request received by the prompt-generation API."""

    task: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    technique: PromptTechnique = PromptTechnique.ZERO_SHOT

    role: Optional[str] = Field(
        default=None,
        max_length=1000,
    )

    examples: List[PromptExampleRequest] = Field(
        default_factory=list,
        max_length=10,
    )

    context: Optional[str] = Field(
        default=None,
        max_length=10000,
    )

    constraints: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    expected_output: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @field_validator(
        "task",
        "role",
        "context",
        "constraints",
        "expected_output",
    )
    @classmethod
    def strip_text(cls, value):
        if value is None:
            return value

        value = value.strip()

        return value or None


class GeneratedPromptResponse(BaseModel):
    """Response returned after prompt generation."""

    technique: PromptTechnique
    prompt: str
