from typing import Optional

from pydantic import BaseModel, Field, field_validator

from backend.prompts.engine import PromptTechnique


class StructuredAgentResponse(BaseModel):
    intent: str = Field(
        ...,
        description="The detected user intent.",
    )

    response: str = Field(
        ...,
        description="The final response generated for the user.",
    )

    model: str = Field(
        ...,
        description="The model used to generate the response.",
    )


class AgentChatRequest(BaseModel):
    user_id: int = Field(
        ...,
        ge=1,
    )

    conversation_id: Optional[int] = Field(
        default=None,
        ge=1,
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    model: str = Field(
        default="mistral",
        min_length=1,
        max_length=100,
    )

    temperature: float = Field(
        default=0.4,
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
        gt=0,
        le=8192,
    )

    response_format: str = Field(
        default="text",
    )

    technique: PromptTechnique = Field(
        default=PromptTechnique.ZERO_SHOT,
    )

    role: Optional[str] = Field(
        default=None,
        max_length=1000,
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

    examples: Optional[str] = Field(
        default=None,
        max_length=10000,
    )

    @field_validator("response_format")
    @classmethod
    def validate_response_format(cls, value: str) -> str:
        value = value.strip().lower()

        if value not in {"text", "json"}:
            raise ValueError(
                "response_format must be either 'text' or 'json'."
            )

        return value

    @field_validator(
        "role",
        "context",
        "constraints",
        "expected_output",
        "examples",
    )
    @classmethod
    def strip_optional_text(
        cls,
        value: Optional[str],
    ) -> Optional[str]:

        if value is None:
            return None

        value = value.strip()

        return value or None


class AgentChatResponse(BaseModel):
    conversation_id: int
    user_message_id: int
    assistant_message_id: int
    intent: str
    response: str
    model: str
