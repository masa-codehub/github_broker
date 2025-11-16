from __future__ import annotations

from github_broker.domain.agent_config import AgentConfigList
from github_broker.domain.task import Task
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient


class TaskService:
    def __init__(
        self,
        github_client: GitHubClient,
        redis_client: RedisClient,
        agent_configs: AgentConfigList,
    ):
        self.github_client = github_client
        self.redis_client = redis_client
        self.agent_roles = {
            agent.role: agent.persona for agent in agent_configs.get_all()
        }

    def request_task(self, issue: dict) -> None:
        """
        NOTE: This method's logic is temporarily disabled to resolve build errors.
        It needs to be reimplemented based on the new architecture.
        """
        self._create_task(issue)
        return

    def _create_task(self, issue: dict) -> Task:
        return Task(
            issue_id=issue.get("number", 0),
            title=issue.get("title", ""),
            body=issue.get("body", ""),
            html_url=issue.get("html_url", ""),
            labels=[label["name"] for label in issue.get("labels", [])],
        )

    @staticmethod
    def create_from_env() -> TaskService:
        # Import late to avoid circular dependency
        from github_broker.infrastructure.di_container import create_container

        container = create_container()
        return container.resolve(TaskService)
