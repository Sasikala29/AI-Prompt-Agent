from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )


class UserResponse(BaseModel):
    id: int
    name: str
