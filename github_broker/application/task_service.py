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

            branch_name = f"feature/issue-{new_issue.id}"
            self._github_client.create_branch(
                repo_name=self.repo_name,
                branch_name=branch_name
            )

            self._redis_client.set_assignment(agent_id, new_issue.id)

            return TaskResponse(
                issue_id=new_issue.id,
                issue_url=new_issue.html_url,
                title=new_issue.title,
                body=new_issue.body,
                labels=[str(label.name) for label in new_issue.labels],
                branch_name=branch_name
            )

        finally:
            self._redis_client.release_lock()

    def _process_previous_task(self, agent_id: str):
        """
        Checks if the agent had a previous task and marks it as complete.
        """
        previous_issue_id = self._redis_client.get_assignment(agent_id)
        if previous_issue_id:
            print(f"Agent {agent_id} completed issue #{previous_issue_id}. Updating label.")
            self._github_client.update_issue_label(
                repo_name=self.repo_name,
                issue_id=previous_issue_id,
                new_label="needs-review"
            )

    def _select_best_issue(self, capabilities: list[str]):
        """
        Selects the most suitable issue for the agent based on their capabilities.
        """
        open_issues = self._github_client.get_open_issues(repo_name=self.repo_name)
        if not open_issues:
            return None

        # Use a dictionary for efficient O(1) lookup later
        issues_map = {issue.id: issue for issue in open_issues}

        # Use a list comprehension for conciseness
        issues_for_gemini = [
            {
                "id": issue.id,
                "title": issue.title,
                "body": issue.body,
                "labels": [label.name for label in issue.labels],
            }
            for issue in issues_map.values()
        ]

        selected_issue_id = self._gemini_client.select_best_issue_id(
            issues_for_gemini, capabilities
        )

        return issues_map.get(selected_issue_id)

