from pydantic import BaseModel

class AgentConfig(BaseModel):
    role: str
    description: str
