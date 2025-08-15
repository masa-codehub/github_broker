from github import UnknownObjectException
from ..infrastructure.github_client import GitHubClient
from ..infrastructure.redis_client import RedisClient
from ..infrastructure.gemini_client import GeminiClient
from ..interface.models import TaskResponse # Un-comment to use the response model

class TaskService:
    """
    This service contains the core business logic for task assignment.
    """
    def __init__(self, github_client: GitHubClient, redis_client: RedisClient, gemini_client: GeminiClient, repo_name: str):
        self._github_client = github_client
        self._redis_client = redis_client
        self._gemini_client = gemini_client
        self.repo_name = repo_name

    def request_task(self, agent_id: str, capabilities: list[str]) -> TaskResponse | None:
        """
        Orchestrates the process of assigning a new task to a worker agent.

        Returns:
            A TaskResponse object if a task is assigned.
            None if no suitable task is found.

        Raises:
            Exception: If the server is busy (lock could not be acquired).
        """
        if not self._redis_client.acquire_lock():
            raise Exception("Server is busy. Please try again later.")

        try:
            self._process_previous_task(agent_id)

            new_issue = self._select_best_issue(capabilities)
            if not new_issue:
                return None

            # Add the in-progress label to mark the issue as assigned
            in_progress_label = f"in-progress:{agent_id}"
            self._github_client.add_label(
                repo_name=self.repo_name,
                issue_id=new_issue.id,
                label=in_progress_label
            )

            branch_name = f"feature/issue-{new_issue.id}"
            self._github_client.create_branch(
                repo_name=self.repo_name,
                branch_name=branch_name
            )

            self._redis_client.set_assignment(agent_id, new_issue.id)

            return TaskResponse(