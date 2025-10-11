from enum import Enum

from pydantic import BaseModel, Field, HttpUrl

from github_broker.domain.task import TaskCandidateStatus


class AgentTaskRequest(BaseModel):
    agent_id: str
    agent_role: str
    timeout: int | None = Field(
        default=120,
        description="リクエストのタイムアウト（秒）。クライアント側で指定するためのオプションです。",
    )


class TaskType(str, Enum):
    DEVELOPMENT = "development"
    REVIEW = "review"
    FIX = "fix"


class TaskResponse(BaseModel):
    issue_id: int
    issue_url: HttpUrl
    title: str
    body: str
    labels: list[str]
    branch_name: str
    prompt: str
    task_type: TaskType = TaskType.DEVELOPMENT
    gemini_response: str | None = None


class CreateFixTaskRequest(BaseModel):
    pull_request_number: int
    review_comments: str


class TaskCandidate(BaseModel):
    issue_id: int
    agent_id: str
    status: TaskCandidateStatus = Field(default=TaskCandidateStatus.PENDING)
