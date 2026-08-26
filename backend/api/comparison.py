from fastapi import APIRouter, HTTPException

from backend.schemas.comparison import (
    PromptComparisonRequest,
    PromptComparisonResponse,
)
from backend.services.comparison_service import PromptComparisonService


router = APIRouter(
    prefix="/api/v1/comparison",
    tags=["Prompt Comparison"],
)

comparison_service = PromptComparisonService()


@router.post(
    "/",
    response_model=PromptComparisonResponse,
)
async def compare_prompts(
    request: PromptComparisonRequest,
) -> PromptComparisonResponse:
    """
    Compare multiple prompt engineering techniques
    against the same task.
    """

    try:
        return await comparison_service.compare(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"PROMPT COMPARISON ERROR: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Prompt comparison failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        ) from exc