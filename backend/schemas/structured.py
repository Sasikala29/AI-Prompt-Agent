from typing import Any, Dict

from pydantic import BaseModel, Field


class StructuredOutputRequest(BaseModel):
    """
    Defines the expected structured-output configuration.
    """

    content: str = Field(
        ...,
        min_length=1,
        description="Raw LLM response that should contain JSON."
    )

    required_fields: list[str] = Field(
        default_factory=list,
        description="Fields that must exist in the resulting JSON object."
    )


class StructuredOutputResponse(BaseModel):
    """
    Standardized result returned by the structured-output service.
    """

    success: bool
    data: Dict[str, Any] | None = None
    raw_content: str
    error: str | None = None