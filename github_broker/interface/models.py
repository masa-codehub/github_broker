from pydantic import BaseModel, HttpUrl


class AgentTaskRequest(BaseModel):
    agent_id: str
    capabilities: list[str]


class TaskResponse(BaseModel):
    issue_id: int
    issue_url: HttpUrl
    title: str
    body: str
    labels: list[str]
    branch_name: str
