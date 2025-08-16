from github import UnknownObjectException
from ..infrastructure.github_client import GitHubClient
from ..infrastructure.redis_client import RedisClient
from ..infrastructure.gemini_client import GeminiClient
from ..interface.models import TaskResponse
import logging
import re

# --- Pre-compiled Regex Patterns for parsing issue body ---
# This improves performance and readability.
# The pattern looks for a markdown H2 header (##) followed by the specific title,
# captures the content on the next lines until it hits another H2 header or the end of the string.
BRANCH_PATTERN = re.compile(r"^##\s+ブランチ名\s*?\n(.*?)(?=\n##|\Z)", re.MULTILINE | re.DOTALL)
DELIVERABLES_PATTERN = re.compile(r"^##\s+成果物\s*?\n(.*?)(?=\n##|\Z)", re.MULTILINE | re.DOTALL)
# ---------------------------------------------------------

class TaskService:
    """
    This service contains the core business logic for task assignment.
    It uses GitHub labels as the source of truth for task status and Redis for locking.
    """
    def __init__(self, github_client: GitHubClient, redis_client: RedisClient, gemini_client: GeminiClient, repo_name: str):
        self._github_client = github_client
        self._redis_client = redis_client
        self._gemini_client = gemini_client
        self.repo_name = repo_name

    def _parse_issue_body(self, body: str | None) -> tuple[str | None, str | None]:
        if not body:
            return None, None
        
        normalized_body = body.replace('\r\n', '\n')

        branch_match = BRANCH_PATTERN.search(normalized_body)
        deliverables_match = DELIVERABLES_PATTERN.search(normalized_body)

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
        in_progress_label = f"in-progress:{agent_id}"
        previous_issue = self._github_client.find_issue_by_label(repo_name=self.repo_name, label=in_progress_label)

        if previous_issue:
            previous_issue_number = previous_issue.number
            logging.info(f"Agent {agent_id} completed issue #{previous_issue_number}. Updating labels.")
            try:
                self._github_client.remove_label(repo_name=self.repo_name, issue_id=previous_issue_number, label=in_progress_label)
                self._github_client.add_label(repo_name=self.repo_name, issue_id=previous_issue_number, label="needs-review")
            except UnknownObjectException:
                logging.warning(f"Error: Previous issue #{previous_issue_number} not found on GitHub during label update.")
        else:
            logging.info(f"No previous in-progress task found for agent {agent_id}.")


    def _select_best_issue(self, capabilities: list[str]):
        open_issues = self._github_client.get_open_issues(repo_name=self.repo_name)
        if not open_issues:
            logging.info("Step 1: No open issues found after initial filtering in GitHubClient.")
            return None
        logging.info(f"Step 1: Found {len(open_issues)} issues from GitHubClient.")

        logging.info("Step 2: Checking for task readiness (branch name and deliverables)...")
        ready_issues = []
        for issue in open_issues:
            branch_name, deliverables = self._parse_issue_body(issue.body)
            is_ready = bool(branch_name and deliverables)
            
            if is_ready:
                logging.info(f"  - Issue #{issue.number} ('{issue.title}') is READY.")
                ready_issues.append(issue)
            else:
                reasons = []
                if not branch_name:
                    reasons.append("Missing '## ブランチ名' section")
                if not deliverables:
                    reasons.append("Missing '## 成果物' section")
                logging.warning(f"  - Issue #{issue.number} ('{issue.title}') is NOT READY. Reason(s): {', '.join(reasons)}.")

        if not ready_issues:
            logging.warning("Step 2: No issues were ready for assignment after checking their body content.")
            return None
        logging.info(f"Step 2: Found {len(ready_issues)} ready issues.")

        logging.info("Step 3: Passing ready issues to Gemini for final selection...")
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
        
        if selected_issue_number:
            logging.info(f"Step 3: Gemini selected Issue #{selected_issue_number}.")
        else:
            logging.warning("Step 3: Gemini did not select an issue.")

        return issues_map.get(selected_issue_number)