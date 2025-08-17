import logging
import re
import time

from github import UnknownObjectException

from ..infrastructure.executors.gemini_executor import GeminiExecutor
from ..infrastructure.github_client import GitHubClient
from ..infrastructure.redis_client import RedisClient
from ..interface.models import TaskResponse


BRANCH_PATTERN = re.compile(r'## ブランチ名\s*(.+?)\s*(?:##|$)', re.IGNORECASE | re.DOTALL)
DELIVERABLES_PATTERN = re.compile(r'## 成果物\s*(.+?)\s*(?:##|$)', re.IGNORECASE | re.DOTALL)


class TaskService:
    GITHUB_INDEX_WAIT_SECONDS = 15 # GitHub検索インデックスの更新を待つ秒数

    def __init__(self, github_client: GitHubClient, redis_client: RedisClient, gemini_executor: GeminiExecutor, repo_name: str):
        self._github_client = github_client
        self._redis_client = redis_client
        self._gemini_executor = gemini_executor
        self.repo_name = repo_name

    def _parse_issue_body(self, body: str | None) -> tuple[str | None, str | None]:
        if not body:
            return None, None
        normalized_body = body.replace("\r\n", "\n")
        branch_match = BRANCH_PATTERN.search(normalized_body)
        deliverables_match = DELIVERABLES_PATTERN.search(normalized_body)
        branch_name = branch_match.group(1).strip() if branch_match else None
        deliverables = deliverables_match.group(1).strip() if deliverables_match else None
        return branch_name, deliverables

    def _is_task_ready(self, issue) -> bool:
        _, deliverables = self._parse_issue_body(issue.body)
        return bool(deliverables)

    def request_task(self, agent_id: str, capabilities: list[str]) -> TaskResponse | None:
        if not self._redis_client.acquire_lock():
            raise Exception("Server is busy. Please try again later.")
        
        try:
            # --- 1. 前のタスクを処理 ---
            previous_task_processed = self._process_previous_task(agent_id)
            if previous_task_processed:
                logging.info(f"前回のタスクを処理しました。GitHub検索インデックスの更新を {self.GITHUB_INDEX_WAIT_SECONDS} 秒待ちます...")
                time.sleep(self.GITHUB_INDEX_WAIT_SECONDS)

            # --- 2. 新しいIssueを選択 ---
            try:
                new_issue = self._select_best_issue(capabilities, agent_id)
                if not new_issue:
                    return None
            except UnknownObjectException:
                logging.warning("An error occurred while trying to select a new issue. It might have been deleted or there was a client error.")
                return None

            # --- 3. 選択したIssueをタスクとして割り当て ---
            try:
                issue_number = new_issue.number
                branch_name, _ = self._parse_issue_body(new_issue.body)
                if not branch_name:
                    branch_name = f"feature/issue-{issue_number}"
                
                self._github_client.add_label(repo_name=self.repo_name, issue_id=issue_number, label="in-progress")
                self._github_client.add_label(repo_name=self.repo_name, issue_id=issue_number, label=agent_id)
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

    def _process_previous_task(self, agent_id: str) -> bool:
        """Processes the previous task, returns True if a task was updated."""
        previous_issue = self._github_client.find_issues_by_labels(
            repo_name=self.repo_name, 
            labels=["in-progress", agent_id]
        )
        if previous_issue:
            previous_issue_number = previous_issue.number
            logging.info(f"Agent {agent_id} completed issue #{previous_issue_number}. Updating labels.")
            try:
                self._github_client.remove_label(repo_name=self.repo_name, issue_id=previous_issue_number, label="in-progress")
                self._github_client.remove_label(repo_name=self.repo_name, issue_id=previous_issue_number, label=agent_id)
                self._github_client.add_label(repo_name=self.repo_name, issue_id=previous_issue_number, label="needs-review")
                return True # ラベル更新に成功
            except UnknownObjectException:
                logging.warning(f"Error: Previous issue #{previous_issue_number} not found on GitHub during label update.")
                return False # 更新中にエラー
        else:
            logging.info(f"No previous in-progress task found for agent {agent_id}.")
            return False # 対象のタスクなし

    def _select_best_issue(self, capabilities: list[str], agent_id: str):
        open_issues = self._github_client.get_open_issues(repo_name=self.repo_name)
        if not open_issues:
            logging.info("No open issues found.")
            return None
        
        logging.info(f"Found {len(open_issues)} open issues. Checking for ready tasks...")
        ready_issues = [issue for issue in open_issues if self._is_task_ready(issue)]
        
        if not ready_issues:
            logging.warning(f"No ready issues found. All {len(open_issues)} open issues are missing the '## 成果物' section or it is empty.")
            for issue in open_issues:
                _, deliverables = self._parse_issue_body(issue.body)
                branch, _ = self._parse_issue_body(issue.body)
                logging.info(f"  - Issue #{issue.number} ('{issue.title}') is not ready. Branch: {branch}, Deliverables: {deliverables}")
            return None
        
        # --- 案Aの実装 ---
        logging.info(f"Found {len(ready_issues)} ready issues. Selecting the first one.")
        selected_issue = ready_issues[0]
        logging.info(f"Selected issue #{selected_issue.number} ('{selected_issue.title}').")
        return selected_issue
