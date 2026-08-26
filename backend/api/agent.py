from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.agent import AgentChatRequest, AgentChatResponse
from backend.services.agent_chat_service import AgentChatService


router = APIRouter(
    prefix="/api/agent",
    tags=["AI Agent"],
)


@router.post(
    "/chat",
    response_model=AgentChatResponse,
)
async def agent_chat(
    request: AgentChatRequest,
    db: Session = Depends(get_db),
) -> AgentChatResponse:

    try:
        service = AgentChatService(db)

        return await service.send_message(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {type(exc).__name__}: {exc}",
        ) from exc
