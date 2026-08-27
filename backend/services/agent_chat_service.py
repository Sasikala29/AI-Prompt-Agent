# backend/services/agent_chat_service.py

from sqlalchemy.orm import Session

from backend.prompts.engine import (
    PromptEngine,
    PromptExample,
    PromptRequest,
    PromptTechnique,
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

        # ---------------------------------------------------------
        # Parse examples received from frontend
        # ---------------------------------------------------------

        examples = self._parse_examples(request.examples)

        # ---------------------------------------------------------
        # Automatically provide examples for one-shot/few-shot
        # when frontend does not send them.
        # ---------------------------------------------------------

        if request.technique == PromptTechnique.ONE_SHOT:
            if len(examples) == 0:
                examples = self._default_one_shot_example(
                    request.message
                )

        elif request.technique == PromptTechnique.FEW_SHOT:
            if len(examples) < 2:
                examples = self._default_few_shot_examples(
                    request.message
                )

        # ---------------------------------------------------------
        # Build prompt request
        # ---------------------------------------------------------

        prompt_request = PromptRequest(
            task=request.message,
            technique=request.technique,
            role=request.role,
            context=request.context,
            constraints=request.constraints,
            expected_output=request.expected_output,
            examples=examples,
        )

        # ---------------------------------------------------------
        # Generate technique-specific prompt
        # ---------------------------------------------------------

        generated_prompt = self.prompt_engine.generate(
            prompt_request
        )

        agent_message = generated_prompt.prompt

        # ---------------------------------------------------------
        # Add previous conversation history
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Execute LLM
        # ---------------------------------------------------------

        result = await self.agent_service.run(
            message=agent_message,
            model=request.model,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )

        # ---------------------------------------------------------
        # Save assistant response
        # ---------------------------------------------------------

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

    # =============================================================
    # EXAMPLE PARSER
    # =============================================================

    @staticmethod
    def _parse_examples(
        examples: str | None,
    ) -> list[PromptExample]:

        if not examples or not examples.strip():
            return []

        parsed_examples: list[PromptExample] = []

        # Normalize Windows line endings
        text = examples.replace("\r\n", "\n").strip()

        # Split examples by blank lines
        blocks = text.split("\n\n")

        for block in blocks:

            lines = block.strip().splitlines()

            input_text = None
            output_text = None

            for line in lines:

                stripped = line.strip()

                if stripped.lower().startswith("input:"):
                    input_text = stripped.split(
                        ":", 1
                    )[1].strip()

                elif stripped.lower().startswith("output:"):
                    output_text = stripped.split(
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

    # =============================================================
    # DEFAULT ONE-SHOT EXAMPLE
    # =============================================================

    @staticmethod
    def _default_one_shot_example(
        task: str,
    ) -> list[PromptExample]:
        """
        Provides one generic example when the user selects
        One-shot prompting but does not provide an example.
        """

        return [
            PromptExample(
                input="Explain temperature in LLMs.",
                output=(
                    "Temperature controls the randomness of an LLM. "
                    "Lower values produce more predictable responses, "
                    "while higher values produce more varied responses."
                ),
            )
        ]

    # =============================================================
    # DEFAULT FEW-SHOT EXAMPLES
    # =============================================================

    @staticmethod
    def _default_few_shot_examples(
        task: str,
    ) -> list[PromptExample]:
        """
        Provides multiple examples when the user selects
        Few-shot prompting but does not provide examples.
        """

        return [
            PromptExample(
                input="What does temperature control in an LLM?",
                output=(
                    "Temperature controls the randomness of the "
                    "model's responses."
                ),
            ),
            PromptExample(
                input="What does top-p control in an LLM?",
                output=(
                    "Top-p controls the range of token probabilities "
                    "considered during generation."
                ),
            ),
        ]

    # =============================================================
    # CONVERSATION TITLE
    # =============================================================

    @staticmethod
    def _create_title(message: str) -> str:

        title = " ".join(
            message.strip().split()
        )

        if len(title) > 60:
            return f"{title[:57]}..."

        return title

