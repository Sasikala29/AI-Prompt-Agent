"""
Prompt-generation API endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from backend.schemas.prompts import (
    GeneratedPromptResponse,
    PromptGenerateRequest,
)
from backend.services.prompt_service import PromptService


router = APIRouter(
    prefix="/api/prompts",
    tags=["Prompts"],
)

prompt_service = PromptService()


@router.post(
    "/generate",
    response_model=GeneratedPromptResponse,
    status_code=status.HTTP_200_OK,
)
def generate_prompt(
    request: PromptGenerateRequest,
) -> GeneratedPromptResponse:
    """
    Generate a prompt using the selected prompting technique.
    """

    try:
        result = prompt_service.generate_prompt(request)

        return GeneratedPromptResponse(
            technique=result.technique,
            prompt=result.prompt,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate prompt.",
        ) from exc