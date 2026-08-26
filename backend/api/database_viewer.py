from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.models.user import User
from backend.models.conversation import Conversation
from backend.models.message import Message


router = APIRouter(
    prefix="/api/database",
    tags=["Database Viewer"],
)


@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
):
    users = db.scalars(
        select(User).order_by(User.id)
    ).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "created_at": user.created_at,
        }
        for user in users
    ]


@router.get("/conversations")
def get_conversations(
    db: Session = Depends(get_db),
):
    conversations = db.scalars(
        select(Conversation)
        .order_by(Conversation.id.desc())
    ).all()

    return [
        {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "provider": conversation.provider,
            "model": conversation.model,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
        for conversation in conversations
    ]


@router.get("/messages")
def get_messages(
    db: Session = Depends(get_db),
):
    messages = db.scalars(
        select(Message)
        .order_by(Message.id.desc())
    ).all()

    return [
        {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "role": message.role,
            "content": message.content,
            "prompt_technique": message.prompt_technique,
            "model": message.model,
            "temperature": message.temperature,
            "top_p": message.top_p,
            "max_tokens": message.max_tokens,
            "response_format": message.response_format,
            "created_at": message.created_at,
        }
        for message in messages
    ]
