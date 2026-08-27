from sqlalchemy.orm import Session

from backend.prompts.engine import (
    PromptEngine,
    PromptExample,
    PromptRequest,
)
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
        self.prompt_engine = PromptEngine()

    def _build_prompt(
        self,
        request: ChatMessageRequest,
    ) -> str:
        examples = [
            PromptExample(
                input=example.input,
                output=example.output,
            )
            for example in request.examples
        ]

        prompt_request = PromptRequest(
            task=request.message,
            technique=request.prompt_technique,
            role=request.role,
            examples=examples,
            context=request.context,
            constraints=request.constraints,
            expected_output=request.expected_output,
        )

        generated_prompt = self.prompt_engine.generate(
            prompt_request
        )

        return generated_prompt.prompt

    def _build_llm_messages(
        self,
        request: ChatMessageRequest,
        previous_messages,
    ) -> list[LLMMessage]:

        memory = self.memory_service.get_memory(
            request.user_id
        )

        llm_messages: list[LLMMessage] = []

        # --------------------------------------------------------
        # USER MEMORY
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # PREVIOUS CONVERSATION HISTORY
        # --------------------------------------------------------

        llm_messages.extend(
            LLMMessage(
                role=message.role,
                content=message.content,
            )
            for message in previous_messages
        )

        # --------------------------------------------------------
        # CURRENT USER REQUEST
        # --------------------------------------------------------

        llm_messages.append(
            LLMMessage(
                role="user",
                content=self._build_prompt(request),
            )
        )

        return llm_messages

    async def send_message(
        self,
        request: ChatMessageRequest,
    ) -> ChatMessageResponse:

        conversation = None

        # --------------------------------------------------------
        # FIND EXISTING CONVERSATION
        # --------------------------------------------------------

        if request.conversation_id is not None:
            conversation = self.repository.get_conversation(
                request.conversation_id,
                request.user_id,
            )

            if conversation is None:
                raise ValueError(
                    f"Conversation {request.conversation_id} was not found."
                )

        # --------------------------------------------------------
        # CREATE NEW CONVERSATION
        # --------------------------------------------------------

        if conversation is None:
            title = self._create_title(
                request.message
            )

            conversation = self.repository.create_conversation(
                user_id=request.user_id,
                title=title,
                provider="ollama",
                model=request.model,
            )

        # --------------------------------------------------------
        # GET ONLY PREVIOUS MESSAGES
        #
        # IMPORTANT:
        # Do this before saving the current user message.
        # The current request is added separately by
        # _build_llm_messages().
        # --------------------------------------------------------

        previous_messages = list(
            conversation.messages
        )

        # --------------------------------------------------------
        # BUILD LLM CONTEXT
        # --------------------------------------------------------

        llm_messages = self._build_llm_messages(
            request,
            previous_messages,
        )

        # --------------------------------------------------------
        # BUILD LLM REQUEST
        # --------------------------------------------------------

        llm_request = LLMRequest(
            model=request.model,
            messages=llm_messages,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
            stream=False,
        )

        # --------------------------------------------------------
        # CALL LLM
        # --------------------------------------------------------

        response = await self.llm_service.generate(
            llm_request
        )

        # --------------------------------------------------------
        # SAVE USER MESSAGE
        #
        # Save it only after the LLM context has been built.
        # This prevents the current message from being included
        # twice in the LLM request.
        # --------------------------------------------------------

        user_message = self.repository.add_message(
            conversation=conversation,
            role="user",
            content=request.message,
            prompt_technique=request.prompt_technique.value,
            model=request.model,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )

        # --------------------------------------------------------
        # SAVE ASSISTANT RESPONSE
        # --------------------------------------------------------

        assistant_message = self.repository.add_message(
            conversation=conversation,
            role="assistant",
            content=response.content,
            prompt_technique=request.prompt_technique.value,
            model=response.model,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )

        # --------------------------------------------------------
        # RETURN RESPONSE
        # --------------------------------------------------------

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

        conversation = None

        # --------------------------------------------------------
        # FIND EXISTING CONVERSATION
        # --------------------------------------------------------

        if request.conversation_id is not None:
            conversation = self.repository.get_conversation(
                request.conversation_id,
                request.user_id,
            )

            if conversation is None:
                raise ValueError(
                    f"Conversation {request.conversation_id} was not found."
                )

        # --------------------------------------------------------
        # CREATE NEW CONVERSATION
        # --------------------------------------------------------

        if conversation is None:
            title = self._create_title(
                request.message
            )

            conversation = self.repository.create_conversation(
                user_id=request.user_id,
                title=title,
                provider="ollama",
                model=request.model,
            )

        # --------------------------------------------------------
        # GET PREVIOUS MESSAGES
        #
        # IMPORTANT:
        # Current user message is NOT saved yet.
        # --------------------------------------------------------

        previous_messages = list(
            conversation.messages
        )

        # --------------------------------------------------------
        # BUILD LLM CONTEXT
        # --------------------------------------------------------

        llm_messages = self._build_llm_messages(
            request,
            previous_messages,
        )

        # --------------------------------------------------------
        # BUILD STREAMING LLM REQUEST
        # --------------------------------------------------------

        llm_request = LLMRequest(
            model=request.model,
            messages=llm_messages,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
            stream=True,
        )

        # --------------------------------------------------------
        # STREAM RESPONSE
        # --------------------------------------------------------

        chunks: list[str] = []

        try:
            async for chunk in self.llm_service.stream(
                llm_request
            ):
                chunks.append(chunk)
                yield chunk

        except Exception:
            # Do not save an incomplete assistant response
            # when the LLM request fails during streaming.
            raise

        # --------------------------------------------------------
        # COMPLETE RESPONSE
        # --------------------------------------------------------

        complete_response = "".join(chunks)

        # --------------------------------------------------------
        # SAVE USER MESSAGE
        #
        # Save after the LLM context was built so the current
        # question does not get duplicated in the request.
        # --------------------------------------------------------

        self.repository.add_message(
            conversation=conversation,
            role="user",
            content=request.message,
            prompt_technique=request.prompt_technique.value,
            model=request.model,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )

        # --------------------------------------------------------
        # SAVE ASSISTANT RESPONSE
        # --------------------------------------------------------

        self.repository.add_message(
            conversation=conversation,
            role="assistant",
            content=complete_response,
            prompt_technique=request.prompt_technique.value,
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

        conversations = self.repository.list_conversations(
            user_id
        )

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
    def _create_title(
        message: str,
    ) -> str:

        title = " ".join(
            message.strip().split()
        )

        if len(title) > 60:
            return f"{title[:57]}..."

        return title