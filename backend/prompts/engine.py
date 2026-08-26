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
    """Normalized result returned by the prompt engine."""

    technique: PromptTechnique
    prompt: str


class PromptEngine:
    """
    Central prompt-generation service.

    The engine selects the appropriate prompt-building strategy
    based on the requested technique.
    """

    def generate(
        self,
        request: PromptRequest,
    ) -> GeneratedPrompt:

        if not request.task.strip():
            raise ValueError("Task cannot be empty.")

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

    def _build_zero_shot(
        self,
        request: PromptRequest,
    ) -> str:
        """Build a direct instruction without examples."""

        return request.task.strip()

    def _build_one_shot(
        self,
        request: PromptRequest,
    ) -> str:
        """Build a prompt containing exactly one example."""

        if len(request.examples) < 1:
            raise ValueError(
                "One-shot prompting requires at least one example."
            )

        example = request.examples[0]

        return (
            "Example:\n"
            f"Input: {example.input}\n"
            f"Output: {example.output}\n\n"
            "Task:\n"
            f"{request.task.strip()}"
        )

    def _build_few_shot(
        self,
        request: PromptRequest,
    ) -> str:
        """Build a prompt containing multiple examples."""

        if len(request.examples) < 2:
            raise ValueError(
                "Few-shot prompting requires at least two examples."
            )

        example_blocks = []

        for index, example in enumerate(
            request.examples,
            start=1,
        ):
            example_blocks.append(
                f"Example {index}:\n"
                f"Input: {example.input}\n"
                f"Output: {example.output}"
            )

        examples_text = "\n\n".join(example_blocks)

        return (
            f"{examples_text}\n\n"
            "Task:\n"
            f"{request.task.strip()}"
        )

    def _build_role_based(
        self,
        request: PromptRequest,
    ) -> str:
        """Build a prompt using an explicit expert role."""

        if not request.role or not request.role.strip():
            raise ValueError(
                "Role-based prompting requires a role."
            )

        return (
            f"You are {request.role.strip()}.\n\n"
            "Task:\n"
            f"{request.task.strip()}"
        )

    def _build_chain_of_thought(
        self,
        request: PromptRequest,
    ) -> str:
        """
        Build a reasoning-oriented prompt.

        The prompt asks the model to reason carefully before
        producing the final answer.
        """

        return (
            "Analyze the problem carefully and reason through "
            "the solution step by step before providing the "
            "final answer.\n\n"
            "Task:\n"
            f"{request.task.strip()}"
        )

    def _build_structured(
        self,
        request: PromptRequest,
    ) -> str:
        """Build a structured prompt from reusable sections."""

        sections = []

        if request.role and request.role.strip():
            sections.append(
                "ROLE:\n"
                f"{request.role.strip()}"
            )

        if request.context and request.context.strip():
            sections.append(
                "CONTEXT:\n"
                f"{request.context.strip()}"
            )

        sections.append(
            "TASK:\n"
            f"{request.task.strip()}"
        )

        if request.constraints and request.constraints.strip():
            sections.append(
                "CONSTRAINTS:\n"
                f"{request.constraints.strip()}"
            )

        if request.expected_output and request.expected_output.strip():
            sections.append(
                "EXPECTED OUTPUT:\n"
                f"{request.expected_output.strip()}"
            )

        if request.examples:
            example_blocks = []

            for index, example in enumerate(
                request.examples,
                start=1,
            ):
                example_blocks.append(
                    f"Example {index}:\n"
                    f"Input: {example.input}\n"
                    f"Output: {example.output}"
                )

            sections.append(
                "EXAMPLES:\n"
                + "\n\n".join(example_blocks)
            )

        return "\n\n".join(sections)
