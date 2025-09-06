from pydantic import BaseModel, Field, HttpUrl


class AgentTaskRequest(BaseModel):
    agent_id: str
    agent_role: str
    timeout: int | None = Field(
        default=120,
        description="リクエストのタイムアウト（秒）。クライアント側で指定するためのオプションです。",
    )


class TaskResponse(BaseModel):
    issue_id: int
    issue_url: HttpUrl
    title: str
    body: str
    labels: list[str]
    branch_name: str
