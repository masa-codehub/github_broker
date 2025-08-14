from pydantic import BaseModel, HttpUrl
from typing import List

class TaskRequest(BaseModel):
    """
    Represents the request body sent by a worker agent.
    """
    agent_id: str
    capabilities: List[str]

class TaskResponse(BaseModel):
    """
    Represents the successful response sent to the worker agent.
    """
    issue_id: int
    issue_url: HttpUrl
    title: str
    body: str
    labels: List[str]
    branch_name: str
