from pydantic import BaseModel, Field


class AgentDefinition(BaseModel):
    """
    Defines the configuration for a single agent role.
    """
    role: str = Field(..., description="The unique role name of the agent (e.g., BACKENDCODER).")
    description: str = Field(..., description="A brief description of the agent's responsibilities.")
    prompt: str | None = Field(None, description="The full system prompt/persona for the agent.")

class AgentConfig(BaseModel):
    """
    The root configuration model for all agents.
    """
    agents: list[AgentDefinition] = Field(..., description="A list of all agent definitions.")
