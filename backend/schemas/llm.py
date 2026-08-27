"""
Common LLM request and response schemas.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator


class LLMMessage(BaseModel):
    role: str = Field(..., min_length=1)
    content: str = Field(default="")

    # Used when assistant requests a tool
    tool_calls: Optional[list[dict[str, Any]]] = None

    # Required when role="tool"
    tool_call_id: Optional[str] = None


class LLMTool(BaseModel):
    type: str = "function"
    function: dict[str, Any]


class LLMToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    tool_call_id: str


class LLMRequest(BaseModel):
    model: str = Field(..., min_length=1)

    messages: List[LLMMessage] = Field(
        ...,
        min_length=1,
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
        gt=0,
        le=8192,
    )

    response_format: str = Field(default="text")

    stream: bool = False

    tools: list[LLMTool] = Field(default_factory=list)

    @field_validator("response_format")
    @classmethod
    def validate_response_format(cls, value: str) -> str:
        value = value.strip().lower()

        allowed = {"text", "json"}

        if value not in allowed:
            raise ValueError(
                "response_format must be either 'text' or 'json'."
            )

        return value


class LLMResponse(BaseModel):
    provider: str
    model: str
    content: str
    execution_time_ms: float

    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    response_format: str = "text"

    tool_calls: list[LLMToolCall] = Field(
        default_factory=list,
    )

    raw_response: dict[str, Any] | None = None
