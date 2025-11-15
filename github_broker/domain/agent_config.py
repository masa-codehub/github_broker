from __future__ import annotations

from pydantic import BaseModel, Field


class AgentDefinition(BaseModel):
    role: str = Field(..., description="The role of the agent.")
    persona: str = Field(..., description="The persona of the agent.")
    # Eventually, we can add more fields here, like the tools available to the agent.


class AgentConfigList(BaseModel):
    agents: list[AgentDefinition] = Field(
        default_factory=list, description="A list of agent definitions."
    )

    def get_all(self) -> list[AgentDefinition]:
        return self.agents

    def find_by_role(self, role: str) -> AgentDefinition | None:
        for agent in self.agents:
            if agent.role == role:
                return agent
        return None
