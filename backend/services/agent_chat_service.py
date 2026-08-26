from sqlalchemy.orm import Session

from backend.prompts.engine import (
    PromptEngine,
    PromptExample,
    PromptRequest,
)
from backend.repositories.conversation_repository import ConversationRepository
from backend.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
)
from backend.services.agent_service import AgentService


class AgentChatService:
    """
    Coordinates prompt engineering, agent execution,
    model parameters, and persistent conversation history.
    """

    def __init__(self, db: Session) -> None:
        self.repository = ConversationRepository(db)
        self.agent_service = AgentService()
        self.prompt_engine = PromptEngine()

    async def send_message(
        self,
        request: AgentChatRequest,
    ) -> AgentChatResponse:

        conversation = None

        if request.conversation_id is not None:
            conversation = self.repository.get_conversation(
                request.conversation_id,
                request.user_id,
            )

            if conversation is None:
                raise ValueError("Conversation not found.")

        if conversation is None:
            conversation = self.repository.create_conversation(
                user_id=request.user_id,
                title=self._create_title(request.message),
                provider="ollama",
                model=request.model,
            )

        previous_messages = list(conversation.messages)

        user_message = self.repository.add_message(
            conversation=conversation,
            role="user",
            content=request.message,
            prompt_technique=request.technique.value,
            model=request.model,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )

        examples = self._parse_examples(request.examples)

        prompt_request = PromptRequest(
            task=request.message,
            technique=request.technique,
            role=request.role,
            context=request.context,
            constraints=request.constraints,
            expected_output=request.expected_output,
            examples=examples,
        )

        generated_prompt = self.prompt_engine.generate(
            prompt_request
        )

        agent_message = generated_prompt.prompt

        if previous_messages:
            history = "\n".join(
                f"{message.role}: {message.content}"
                for message in previous_messages
            )

            agent_message = (
                "Conversation history:\n"
                f"{history}\n\n"
                "Current prompt:\n"
                f"{generated_prompt.prompt}"
            )

        result = await self.agent_service.run(
            message=agent_message,
            model=request.model,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )

        assistant_message = self.repository.add_message(
            conversation=conversation,
            role="assistant",
            content=result.response,
            prompt_technique=request.technique.value,
            model=result.model,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )

        return AgentChatResponse(
            conversation_id=conversation.id,
            user_message_id=user_message.id,
            assistant_message_id=assistant_message.id,
            intent=result.intent,
            response=result.response,
            model=result.model,
        )

    @staticmethod
    def _parse_examples(
        examples: str | None,
    ) -> list[PromptExample]:

        if not examples or not examples.strip():
            return []

        parsed_examples = []

        for block in examples.split("\n\n"):
            lines = block.strip().splitlines()

            input_text = None
            output_text = None

            for line in lines:
                if line.lower().startswith("input:"):
                    input_text = line.split(
                        ":", 1
                    )[1].strip()

                elif line.lower().startswith("output:"):
                    output_text = line.split(
                        ":", 1
                    )[1].strip()

            if input_text and output_text:
                parsed_examples.append(
                    PromptExample(
                        input=input_text,
                        output=output_text,
                    )
                )

        return parsed_examples

    @staticmethod
    def _create_title(message: str) -> str:
        title = " ".join(message.strip().split())

        if len(title) > 60:
            return f"{title[:57]}..."

        return title
