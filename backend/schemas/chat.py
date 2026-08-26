from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    conversation_id: int | None = Field(
        default=None,
        ge=1,
    )

    user_id: int = Field(
        ...,
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

    response_format: str = Field(
        default="text",
        pattern="^(text|json)$",
    )


class ChatMessageResponse(BaseModel):
    conversation_id: int
    user_message_id: int
    assistant_message_id: int
    response: str
    model: str
    execution_time_ms: float
    total_tokens: int | None = None


class ConversationSummary(BaseModel):
    id: int
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    prompt_technique: str | None = None
    model: str | None = None
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None
    response_format: str | None = None
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]
