import json
from typing import Any

from backend.schemas.structured import (
    StructuredOutputRequest,
    StructuredOutputResponse,
)


class StructuredOutputService:
    """
    Handles parsing and validation of structured JSON responses
    returned by the LLM.
    """

    @staticmethod
    def parse(
        request: StructuredOutputRequest,
    ) -> StructuredOutputResponse:
        raw_content = request.content.strip()

        if not raw_content:
            return StructuredOutputResponse(
                success=False,
                raw_content=request.content,
                error="LLM returned an empty response.",
            )

        try:
            data: Any = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            return StructuredOutputResponse(
                success=False,
                raw_content=request.content,
                error=f"Invalid JSON returned by the model: {exc.msg}.",
            )

        if not isinstance(data, dict):
            return StructuredOutputResponse(
                success=False,
                raw_content=request.content,
                error="Structured output must be a JSON object.",
            )

        missing_fields = [
            field
            for field in request.required_fields
            if field not in data
        ]

        if missing_fields:
            return StructuredOutputResponse(
                success=False,
                raw_content=request.content,
                error=(
                    "Required fields are missing: "
                    + ", ".join(missing_fields)
                ),
            )

        return StructuredOutputResponse(
            success=True,
            data=data,
            raw_content=raw_content,
        )