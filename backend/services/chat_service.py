from sqlalchemy.orm import Session

from backend.repositories.conversation_repository import ConversationRepository
from backend.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationDetailResponse,
    ConversationSummary,
    MessageResponse,
)
from backend.schemas.llm import LLMMessage, LLMRequest
from backend.services.llm_service import LLMService
from backend.services.memory_service import MemoryService


class ChatService:

    def __init__(
        self,
        db: Session,
        llm_service: LLMService | None = None,
    ):
        self.repository = ConversationRepository(db)
        self.llm_service = llm_service or LLMService()
        self.memory_service = MemoryService()

    async def send_message(
        self,
        request: ChatMessageRequest,
    ) -> ChatMessageResponse:

        conversation = None

        if request.conversation_id is not None:
            conversation = self.repository.get_conversation(
                request.conversation_id,
                request.user_id,
            )

            if conversation is None:
                raise ValueError(
                    f"Conversation {request.conversation_id} was not found."
                )

        if conversation is None:
            title = self._create_title(request.message)

            conversation = self.repository.create_conversation(
                user_id=request.user_id,
                title=title,
                provider="ollama",
                model=request.model,
            )

        previous_messages = list(conversation.messages)

        user_message = self.repository.add_message(
            conversation=conversation,
            role="user",
            content=request.message,
            model=request.model,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )

        memory = self.memory_service.get_memory(request.user_id)

        llm_messages: list[LLMMessage] = []

        if memory:
            memory_text = "\n".join(
                f"{key}: {value}"
                for key, value in memory.items()
            )

            llm_messages.append(
                LLMMessage(
                    role="system",
                    content=(
                        "User memory. Use this information when "
                        "relevant and do not invent additional facts.\n"
                        f"{memory_text}"
                    ),
                )
            )

        llm_messages.extend(
            LLMMessage(
                role=message.role,
                content=message.content,
            )
            for message in previous_messages
        )

        llm_messages.append(
            LLMMessage(
                role="user",
                content=request.message,
            )
        )

        llm_request = LLMRequest(
            model=request.model,
            messages=llm_messages,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
            stream=False,
        )

        response = await self.llm_service.generate(llm_request)

        assistant_message = self.repository.add_message(
            conversation=conversation,
            role="assistant",
            content=response.content,
            model=response.model,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )

        return ChatMessageResponse(
            conversation_id=conversation.id,
            user_message_id=user_message.id,
            assistant_message_id=assistant_message.id,
            response=response.content,
            model=response.model,
            execution_time_ms=response.execution_time_ms,
            total_tokens=response.total_tokens,
        )

    async def stream_message(
        self,
        request: ChatMessageRequest,
    ):
        """
        Stream an LLM response while preserving conversation history.

        The complete response is persisted to SQLite after streaming
        finishes successfully.
        """

        conversation = None

        if request.conversation_id is not None:
            conversation = self.repository.get_conversation(
                request.conversation_id,
                request.user_id,
            )

            if conversation is None:
                raise ValueError(
                    f"Conversation {request.conversation_id} was not found."
                )

        if conversation is None:
            title = self._create_title(request.message)

            conversation = self.repository.create_conversation(
                user_id=request.user_id,
                title=title,
                provider=(
                    "groq"
                    if request.model.lower()
                    == "llama-3.1-8b-instant"
                    else "ollama"
                ),
                model=request.model,
            )

        previous_messages = list(conversation.messages)

        user_message = self.repository.add_message(
            conversation=conversation,
            role="user",
            content=request.message,
            model=request.model,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )

        memory = self.memory_service.get_memory(request.user_id)

        llm_messages: list[LLMMessage] = []

        if memory:
            memory_text = "\n".join(
                f"{key}: {value}"
                for key, value in memory.items()
            )

            llm_messages.append(
                LLMMessage(
                    role="system",
                    content=(
                        "User memory. Use this information when "
                        "relevant and do not invent additional facts.\n"
                        f"{memory_text}"
                    ),
                )
            )

        llm_messages.extend(
            LLMMessage(
                role=message.role,
                content=message.content,
            )
            for message in previous_messages
        )

        llm_messages.append(
            LLMMessage(
                role="user",
                content=request.message,
            )
        )

        llm_request = LLMRequest(
            model=request.model,
            messages=llm_messages,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
            stream=True,
        )

        chunks: list[str] = []

        async for chunk in self.llm_service.stream(llm_request):
            chunks.append(chunk)
            yield chunk

        complete_response = "".join(chunks)

        self.repository.add_message(
            conversation=conversation,
            role="assistant",
            content=complete_response,
            model=request.model,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )


    def list_conversations(
        self,
        user_id: int,
    ) -> list[ConversationSummary]:

        conversations = self.repository.list_conversations(user_id)

        return [
            ConversationSummary(
                id=conversation.id,
                title=conversation.title,
                provider=conversation.provider,
                model=conversation.model,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            )
            for conversation in conversations
        ]

    def get_conversation(
        self,
        conversation_id: int,
        user_id: int,
    ) -> ConversationDetailResponse | None:

        conversation = self.repository.get_conversation(
            conversation_id,
            user_id,
        )

        if conversation is None:
            return None

        return ConversationDetailResponse(
            id=conversation.id,
            title=conversation.title,
            provider=conversation.provider,
            model=conversation.model,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[
                MessageResponse(
                    id=message.id,
                    role=message.role,
                    content=message.content,
                    prompt_technique=message.prompt_technique,
                    model=message.model,
                    temperature=message.temperature,
                    top_p=message.top_p,
                    max_tokens=message.max_tokens,
                    response_format=message.response_format,
                    created_at=message.created_at,
                )
                for message in conversation.messages
            ],
        )

    def delete_conversation(
        self,
        conversation_id: int,
        user_id: int,
    ) -> bool:

        return self.repository.delete_conversation(
            conversation_id,
            user_id,
        )

    @staticmethod
    def _create_title(message: str) -> str:
        title = " ".join(message.strip().split())

        if len(title) > 60:
            return f"{title[:57]}..."

        return title
