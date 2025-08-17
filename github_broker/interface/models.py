
from pydantic import BaseModel, HttpUrl


class TaskRequest(BaseModel):
    """
    Represents the request body sent by a worker agent.
    """

    agent_id: str
    capabilities: list[str]


class TaskResponse(BaseModel):
    """
    Represents the successful response sent to the worker agent.
    """

    issue_id: int
    issue_url: HttpUrl
    title: str
    body: str
    labels: list[str]
    branch_name: str
