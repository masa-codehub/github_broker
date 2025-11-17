"""Domain objects for agents."""
from typing import TypedDict


class AgentDefinition(TypedDict):
    """Represents the definition of an agent."""

    role: str
    description: str
