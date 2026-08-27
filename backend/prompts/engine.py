"""
Reusable prompt engineering engine.

Responsible only for transforming user input into
well-defined prompts using different prompt engineering techniques.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class PromptTechnique(str, Enum):
    """Supported prompt engineering techniques."""

    ZERO_SHOT = "zero-shot"
    ONE_SHOT = "one-shot"
    FEW_SHOT = "few-shot"
    ROLE_BASED = "role-based"
    CHAIN_OF_THOUGHT = "chain-of-thought"
    STRUCTURED = "structured"


@dataclass
class PromptExample:
    """Represents a single input/output example."""

    input: str
    output: str


@dataclass
class PromptRequest:
    """Input required by the prompt engine."""

    task: str

    technique: PromptTechnique = PromptTechnique.ZERO_SHOT

    role: Optional[str] = None

    examples: List[PromptExample] = field(default_factory=list)

    context: Optional[str] = None

    constraints: Optional[str] = None

    expected_output: Optional[str] = None


@dataclass
class GeneratedPrompt:
    """Normalized prompt returned by the prompt engine."""

    technique: PromptTechnique
    prompt: str


class PromptEngine:
    """
    Central prompt-generation service.

    Supported techniques:
    - Zero-shot
    - One-shot
    - Few-shot
    - Role-based
    - Chain-of-thought
    - Structured prompting
    """

    RESPONSE_STYLE = """
RESPONSE STYLE RULES:

- Answer the user's actual request directly.
- Respond naturally like a helpful AI assistant.
- Keep the response clear, concise, and readable.
- Use short paragraphs when appropriate.
- Use headings only when they improve readability.
- Use bullet points for lists.
- Use numbered lists for sequential steps.
- Use code blocks when showing programming code.
- Do NOT use Markdown tables unless explicitly requested.
- Do NOT unnecessarily convert explanations into tables.
- Avoid unnecessary repetition.
- Follow the requested output format exactly.
""".strip()

    def generate(
        self,
        request: PromptRequest,
    ) -> GeneratedPrompt:
        """
        Generate a prompt using the requested technique.
        """

        self._validate_request(request)

        builders = {
            PromptTechnique.ZERO_SHOT: self._build_zero_shot,
            PromptTechnique.ONE_SHOT: self._build_one_shot,
            PromptTechnique.FEW_SHOT: self._build_few_shot,
            PromptTechnique.ROLE_BASED: self._build_role_based,
            PromptTechnique.CHAIN_OF_THOUGHT: self._build_chain_of_thought,
            PromptTechnique.STRUCTURED: self._build_structured,
        }

        builder = builders.get(request.technique)

        if builder is None:
            raise ValueError(
                f"Unsupported prompt technique: {request.technique}"
            )

        prompt = builder(request)

        return GeneratedPrompt(
            technique=request.technique,
            prompt=prompt,
        )

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    def _validate_request(
        self,
        request: PromptRequest,
    ) -> None:
        """Validate common prompt request fields."""

        if not request.task or not request.task.strip():
            raise ValueError("Task cannot be empty.")

        if not isinstance(request.technique, PromptTechnique):
            raise ValueError(
                f"Unsupported prompt technique: {request.technique}"
            )

    def _validate_example(
        self,
        example: PromptExample,
        index: int,
        technique: str,
    ) -> None:
        """Validate a prompt example."""

        if not example.input or not example.input.strip():
            raise ValueError(
                f"{technique} Example {index} input cannot be empty."
            )

        if not example.output or not example.output.strip():
            raise ValueError(
                f"{technique} Example {index} output cannot be empty."
            )

    # ------------------------------------------------------------------
    # COMMON HELPERS
    # ------------------------------------------------------------------

    def _add_optional_section(
        self,
        sections: List[str],
        title: str,
        value: Optional[str],
    ) -> None:
        """Add a section only when a value is provided."""

        if value and value.strip():
            sections.append(
                f"{title}:\n{value.strip()}"
            )

    def _format_example(
        self,
        example: PromptExample,
        index: Optional[int] = None,
    ) -> str:
        """Format a prompt example consistently."""

        if index is not None:
            return (
                f"Example {index}:\n"
                f"Input: {example.input.strip()}\n"
                f"Output: {example.output.strip()}"
            )

        return (
            "Example:\n"
            f"Input: {example.input.strip()}\n"
            f"Output: {example.output.strip()}"
        )

    def _with_response_style(
        self,
        prompt: str,
    ) -> str:
        """Append common response style instructions."""

        return (
            f"{prompt.strip()}\n\n"
            f"{self.RESPONSE_STYLE}"
        )

    def _build_common_sections(
        self,
        request: PromptRequest,
    ) -> List[str]:
        """Build reusable prompt sections."""

        sections: List[str] = []

        self._add_optional_section(
            sections,
            "ROLE",
            request.role,
        )

        self._add_optional_section(
            sections,
            "CONTEXT",
            request.context,
        )

        sections.append(
            f"TASK:\n{request.task.strip()}"
        )

        self._add_optional_section(
            sections,
            "CONSTRAINTS",
            request.constraints,
        )

        self._add_optional_section(
            sections,
            "EXPECTED OUTPUT",
            request.expected_output,
        )

        return sections

    # ------------------------------------------------------------------
    # ZERO-SHOT
    # ------------------------------------------------------------------

    def _build_zero_shot(
        self,
        request: PromptRequest,
    ) -> str:
        """
        Zero-shot prompting.

        Solves the task without providing examples.
        """

        sections = self._build_common_sections(request)

        return self._with_response_style(
            "\n\n".join(sections)
        )

    # ------------------------------------------------------------------
    # ONE-SHOT
    # ------------------------------------------------------------------

    def _build_one_shot(
        self,
        request: PromptRequest,
    ) -> str:
        """
        One-shot prompting.

        Uses exactly one example to demonstrate
        the expected behavior or output style.
        """

        if not request.examples:
            raise ValueError(
                "One-shot prompting requires one example. "
                "Provide an Input and Output example."
            )

        example = request.examples[0]

        self._validate_example(
            example,
            index=1,
            technique="One-shot",
        )

        sections = [
            self._format_example(example),
        ]

        common_sections = self._build_common_sections(request)
        sections.extend(common_sections)

        return self._with_response_style(
            "\n\n".join(sections)
        )

    # ------------------------------------------------------------------
    # FEW-SHOT
    # ------------------------------------------------------------------

    def _build_few_shot(
        self,
        request: PromptRequest,
    ) -> str:
        """
        Few-shot prompting.

        Uses multiple examples to establish
        a clear input/output pattern.
        """

        if len(request.examples) < 2:
            raise ValueError(
                "Few-shot prompting requires at least two examples. "
                "Provide two or more Input/Output examples."
            )

        example_blocks: List[str] = []

        for index, example in enumerate(
            request.examples,
            start=1,
        ):
            self._validate_example(
                example,
                index=index,
                technique="Few-shot",
            )

            example_blocks.append(
                self._format_example(
                    example,
                    index=index,
                )
            )

        sections = [
            "EXAMPLES:\n" + "\n\n".join(example_blocks)
        ]

        common_sections = self._build_common_sections(request)
        sections.extend(common_sections)

        return self._with_response_style(
            "\n\n".join(sections)
        )

    # ------------------------------------------------------------------
    # ROLE-BASED
    # ------------------------------------------------------------------

    def _build_role_based(
        self,
        request: PromptRequest,
    ) -> str:
        """
        Role-based prompting.

        Assigns a specific role/persona to the model
        before executing the task.
        """

        if not request.role or not request.role.strip():
            raise ValueError(
                "Role-based prompting requires a role."
            )

        sections = [
            (
                "ROLE:\n"
                f"You are an expert {request.role.strip()}."
            )
        ]

        self._add_optional_section(
            sections,
            "CONTEXT",
            request.context,
        )

        sections.append(
            f"TASK:\n{request.task.strip()}"
        )

        self._add_optional_section(
            sections,
            "CONSTRAINTS",
            request.constraints,
        )

        self._add_optional_section(
            sections,
            "EXPECTED OUTPUT",
            request.expected_output,
        )

        return self._with_response_style(
            "\n\n".join(sections)
        )

    # ------------------------------------------------------------------
    # CHAIN-OF-THOUGHT
    # ------------------------------------------------------------------

    def _build_chain_of_thought(
        self,
        request: PromptRequest,
    ) -> str:
        """
        Reasoning-oriented prompting.

        Instructs the model to reason carefully internally
        without requesting private chain-of-thought disclosure.
        """

        sections = [
            (
                "REASONING INSTRUCTION:\n"
                "Analyze the problem carefully before producing "
                "the final answer.\n"
                "Break the problem into logical steps internally.\n"
                "Do not expose private chain-of-thought reasoning.\n"
                "Provide only the final answer and a concise "
                "reasoning summary when useful."
            )
        ]

        self._add_optional_section(
            sections,
            "ROLE",
            request.role,
        )

        self._add_optional_section(
            sections,
            "CONTEXT",
            request.context,
        )

        sections.append(
            f"TASK:\n{request.task.strip()}"
        )

        self._add_optional_section(
            sections,
            "CONSTRAINTS",
            request.constraints,
        )

        self._add_optional_section(
            sections,
            "EXPECTED OUTPUT",
            request.expected_output,
        )

        return self._with_response_style(
            "\n\n".join(sections)
        )

    # ------------------------------------------------------------------
    # STRUCTURED
    # ------------------------------------------------------------------

    def _build_structured(
        self,
        request: PromptRequest,
    ) -> str:
        """
        Structured prompting.

        Organizes the request into explicit sections and
        instructs the model to follow the requested format.
        """

        sections = self._build_common_sections(request)

        if request.examples:
            valid_examples: List[str] = []

            for index, example in enumerate(
                request.examples,
                start=1,
            ):
                if (
                    example.input
                    and example.input.strip()
                    and example.output
                    and example.output.strip()
                ):
                    valid_examples.append(
                        self._format_example(
                            example,
                            index=index,
                        )
                    )

            if valid_examples:
                sections.append(
                    "EXAMPLES:\n"
                    + "\n\n".join(valid_examples)
                )

        sections.append(
            (
                "STRUCTURED RESPONSE INSTRUCTION:\n"
                "Follow the requested output structure exactly.\n"
                "Return only the requested information.\n"
                "Do not add unnecessary sections or information."
            )
        )

        return self._with_response_style(
            "\n\n".join(sections)
        )