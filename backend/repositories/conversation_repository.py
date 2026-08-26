from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.models.conversation import Conversation
from backend.models.message import Message


class ConversationRepository:
    """
    Repository responsible for persistence of conversations and messages.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_conversation(
        self,
        user_id: int,
        title: str,
        provider: str,
        model: str,
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            title=title,
            provider=provider,
            model=model,
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_conversation(
        self,
        conversation_id: int,
        user_id: int,
    ) -> Conversation | None:
        statement = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .options(selectinload(Conversation.messages))
        )

        return self.db.scalar(statement)

    def list_conversations(
        self,
        user_id: int,
    ) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def add_message(
        self,
        conversation: Conversation,
        role: str,
        content: str,
        prompt_technique: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        response_format: str | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=content,
            prompt_technique=prompt_technique,
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            response_format=response_format,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def delete_conversation(
        self,
        conversation_id: int,
        user_id: int,
    ) -> bool:
        conversation = self.get_conversation(
            conversation_id,
            user_id,
        )

        if conversation is None:
            return False

        self.db.delete(conversation)
        self.db.commit()

        return True
