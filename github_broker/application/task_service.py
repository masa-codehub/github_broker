from github import UnknownObjectException
from ..infrastructure.github_client import GitHubClient
from ..infrastructure.redis_client import RedisClient
from ..infrastructure.gemini_client import GeminiClient
from ..interface.models import TaskResponse
import logging
import re

class TaskService:
    """
    This service contains the core business logic for task assignment.
    """
    def __init__(self, github_client: GitHubClient, redis_client: RedisClient, gemini_client: GeminiClient, repo_name: str):
        self._github_client = github_client
        self._redis_client = redis_client
        self._gemini_client = gemini_client
        self.repo_name = repo_name

    def _parse_issue_body(self, body: str | None) -> tuple[str | None, str | None]:
        if not body:
            return None, None

        # Use non-capturing group (?:...) and lookahead (?=...) for robust parsing
        branch_match = re.search(r"^##\s+ブランチ名\s*$\n(.*?)(?=\n^##|\Z)", body, re.MULTILINE | re.DOTALL)
        deliverables_match = re.search(r"^##\s+成果物\s*$\n(.*?)(?=\n^##|\Z)", body, re.MULTILINE | re.DOTALL)

        branch_name = branch_match.group(1).strip() if branch_match else None
        deliverables = deliverables_match.group(1).strip() if deliverables_match else None

        return branch_name, deliverables

    def _is_task_ready(self, issue) -> bool:
        branch_name, deliverables = self._parse_issue_body(issue.body)
        return bool(branch_name and deliverables)

    def request_task(self, agent_id: str, capabilities: list[str]) -> TaskResponse | None:
        if not self._redis_client.acquire_lock():
            raise Exception("Server is busy. Please try again later.")

        try:
            self._process_previous_task(agent_id)

            new_issue = self._select_best_issue(capabilities)
            if not new_issue:
                return None

            try:
                issue_number = new_issue.number
                branch_name, _ = self._parse_issue_body(new_issue.body)
                if not branch_name:
                    branch_name = f"feature/issue-{issue_number}"

                in_progress_label = f"in-progress:{agent_id}"
                self._github_client.add_label(repo_name=self.repo_name, issue_id=issue_number, label=in_progress_label)

                self._github_client.create_branch(repo_name=self.repo_name, branch_name=branch_name)

                self._redis_client.set_assignment(agent_id, issue_number)

                return TaskResponse(
                    issue_id=issue_number,
                    issue_url=new_issue.html_url,
                    title=new_issue.title,
                    body=new_issue.body,
                    labels=[str(label.name) for label in new_issue.labels],
                    branch_name=branch_name
                )
            
            except UnknownObjectException:
                logging.warning(f"Issue #{new_issue.number} not found on GitHub during assignment. It might have been deleted. Skipping.")
                return None

        finally:
            self._redis_client.release_lock()

    def _process_previous_task(self, agent_id: str):
        previous_issue_number = self._redis_client.get_assignment(agent_id)
        if previous_issue_number:
            logging.info(f"Agent {agent_id} completed issue #{previous_issue_number}. Updating labels.")
            try:
                in_progress_label = f"in-progress:{agent_id}"
                self._github_client.remove_label(repo_name=self.repo_name, issue_id=previous_issue_number, label=in_progress_label)
                self._github_client.add_label(repo_name=self.repo_name, issue_id=previous_issue_number, label="needs-review")
            except UnknownObjectException:
                logging.warning(f"Error: Previous issue #{previous_issue_number} not found on GitHub. Clearing assignment.")
                self._redis_client.clear_assignment(agent_id)

    def _select_best_issue(self, capabilities: list[str]):
        open_issues = self._github_client.get_open_issues(repo_name=self.repo_name)
        if not open_issues:
            return None

        ready_issues = [issue for issue in open_issues if self._is_task_ready(issue)]
        if not ready_issues:
            return None

        issues_map = {issue.number: issue for issue in ready_issues}

        issues_for_gemini = [
            {
                "id": issue.number,
                "title": issue.title,
                "body": issue.body,
                "labels": [label.name for label in issue.labels],
            }
            for issue in issues_map.values()
        ]

        selected_issue_number = self._gemini_client.select_best_issue_id(issues_for_gemini, capabilities)

        return issues_map.get(selected_issue_number)
