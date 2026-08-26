from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Awaitable


@dataclass
class AgentTool:
    """
    Represents a tool that can be selected and executed by the agent.
    """

    name: str
    description: str
    function: Callable[..., Awaitable[str]]


class ToolRegistry:
    """
    Central registry for all agent tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, AgentTool] = {}

    def register(self, tool: AgentTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> AgentTool | None:
        return self._tools.get(name)

    def all(self) -> list[AgentTool]:
        return list(self._tools.values())

    def descriptions(self) -> list[dict[str, str]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in self._tools.values()
        ]