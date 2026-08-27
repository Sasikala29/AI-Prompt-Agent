from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationDetailResponse,
    ConversationSummary,
)
from backend.services.chat_service import ChatService


router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)


def get_chat_service(
    db: Session = Depends(get_db),
) -> ChatService:
    return ChatService(db)


# ============================================================
# NORMAL CHAT
# ============================================================

@router.post(
    "/chat",
    response_model=ChatMessageResponse,
)
async def send_chat_message(
    request: ChatMessageRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatMessageResponse:

    try:
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
            detail=f"Chat error: {type(exc).__name__}: {exc}",
        ) from exc


# ============================================================
# STREAMING CHAT
# ============================================================

@router.post(
    "/chat/stream",
)
async def stream_chat_message(
    request: ChatMessageRequest,
    service: ChatService = Depends(get_chat_service),
):
    async def generate():

        try:

            async for chunk in service.stream_message(request):

                if chunk:
                    yield chunk

        except ValueError as exc:

            yield f"\n[ERROR] {exc}"

        except RuntimeError as exc:

            yield f"\n[ERROR] {exc}"

        except Exception as exc:

            yield (
                "\n[ERROR] Chat streaming failed: "
                f"{type(exc).__name__}: {exc}"
            )

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================
# LIST CONVERSATIONS
# ============================================================

@router.get(
    "/conversations/{user_id}",
    response_model=list[ConversationSummary],
)
async def list_conversations(
    user_id: int,
    service: ChatService = Depends(get_chat_service),
):
    return service.list_conversations(user_id)


# ============================================================
# GET CONVERSATION
# ============================================================

@router.get(
    "/conversations/{user_id}/{conversation_id}",
    response_model=ConversationDetailResponse,
)
async def get_conversation_details(
    user_id: int,
    conversation_id: int,
    service: ChatService = Depends(get_chat_service),
):

    conversation = service.get_conversation(
        conversation_id,
        user_id,
    )

    if conversation is None:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return conversation


# ============================================================
# DELETE CONVERSATION
# ============================================================

@router.delete(
    "/conversations/{user_id}/{conversation_id}",
)
async def remove_conversation(
    user_id: int,
    conversation_id: int,
    service: ChatService = Depends(get_chat_service),
):

    deleted = service.delete_conversation(
        conversation_id,
        user_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return {
        "message": "Conversation deleted successfully.",
        "conversation_id": conversation_id,
    }