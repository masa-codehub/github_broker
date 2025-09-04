import logging
import os
import time

from github_broker.domain.task import Task
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient
from github_broker.interface.models import TaskResponse

logger = logging.getLogger(__name__)

# --- Constants ---
_GITHUB_INDEXING_WAIT_SECONDS_ENV = "GITHUB_INDEXING_WAIT_SECONDS"
_DEFAULT_GITHUB_INDEXING_WAIT_SECONDS = 15


class TaskService:
    def __init__(
        self,
        redis_client: RedisClient,
        github_client: GitHubClient,
    ):
        self.redis_client = redis_client
        self.github_client = github_client
        self.repo_name = os.getenv("GITHUB_REPOSITORY")
        if not self.repo_name:
            raise ValueError("GITHUB_REPOSITORY環境変数が設定されていません。")

    def complete_previous_task(self, agent_id: str):
        """
        前タスクの完了処理を行います。
        in-progressとagent_idラベルを持つIssueを検索し、それらのラベルを削除し、needs-reviewラベルを付与します。
        """
        logger.info(f"Completing previous task for agent: {agent_id}")
        previous_issues = self.github_client.find_issues_by_labels(
            repo_name=self.repo_name, labels=["in-progress", agent_id]
        )

        for issue in previous_issues:
            logger.info(
                f"Found previous in-progress issue #{issue.number} for agent {agent_id}."
            )
            remove_labels = ["in-progress", agent_id]
            add_labels = ["needs-review"]

            self.github_client.update_issue(
                repo_name=self.repo_name,
                issue_id=issue.number,
                remove_labels=remove_labels,
                add_labels=add_labels,
            )
            logger.info(
                f"Updated labels for issue #{issue.number}: removed {remove_labels}, added {add_labels}."
            )

    def _find_candidates_by_role(self, issues: list, agent_role: str) -> list:
        """指定された役割（role）ラベルを持つIssueをフィルタリングします。"""
        candidate_issues = [issue for issue in issues if agent_role in {label.name for label in issue.labels}]

        if not candidate_issues:
            logger.info(f"No issues found with role label: {agent_role}")

        return candidate_issues

    def _find_first_assignable_task(
        self, candidate_issues: list, agent_id: str
    ) -> TaskResponse | None:
        """候補リストから、最初に割り当て可能なタスクを見つけます。"""
        for issue_obj in sorted(candidate_issues, key=lambda i: i.number):
            task = Task(
                issue_id=issue_obj.number,
                title=issue_obj.title,
                body=issue_obj.body or "",
                html_url=issue_obj.html_url,
                labels=[label.name for label in issue_obj.labels],
            )

            if not task.is_assignable():
                logger.info(
                    f"Issue #{task.issue_id} is not assignable (missing '成果物' section). Skipping."
                )
                continue

            branch_name = task.extract_branch_name()
            if not branch_name:
                logger.warning(
                    f"Issue #{task.issue_id} の本文にブランチ名が見つかりませんでした。このIssueはスキップされます。"
                )
                continue

            lock_key = f"issue_lock_{task.issue_id}"
            if not self.redis_client.acquire_lock(lock_key, "locked", timeout=600):
                logger.warning(
                    f"Issue #{task.issue_id} is locked by another agent. Skipping."
                )
                continue

            try:
                logger.info(
                    f"Lock acquired for issue #{task.issue_id}. Assigning task."
                )
                self.github_client.add_label(
                    self.repo_name, task.issue_id, "in-progress"
                )
                self.github_client.add_label(self.repo_name, task.issue_id, agent_id)
                logger.info(f"Assigned agent '{agent_id}' to issue #{task.issue_id}.")

                self.github_client.create_branch(self.repo_name, branch_name)

                return TaskResponse(
                    issue_id=task.issue_id,
                    issue_url=task.html_url,
                    title=task.title,
                    body=task.body,
                    labels=task.labels,
                    branch_name=branch_name,
                )
            except Exception as e:
                logger.error(
                    f"Failed to process issue #{task.issue_id} after acquiring lock: {e}"
                )
                self.redis_client.release_lock(lock_key)
                raise

        logger.info("No assignable and unlocked issues found.")
        return None

    def request_task(
        self, agent_id: str, agent_role: str
    ) -> TaskResponse | None:
        """
        エージェントの役割（role）に基づいて最適なIssueを探し、タスク情報を返します。
        """
        self.complete_previous_task(agent_id)
        
        try:
            wait_seconds_str = os.getenv(
                _GITHUB_INDEXING_WAIT_SECONDS_ENV, str(_DEFAULT_GITHUB_INDEXING_WAIT_SECONDS)
            )
            wait_seconds = int(wait_seconds_str)
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid value for {_GITHUB_INDEXING_WAIT_SECONDS_ENV}. "
                f"Using default value: {_DEFAULT_GITHUB_INDEXING_WAIT_SECONDS} seconds."
            )
            wait_seconds = _DEFAULT_GITHUB_INDEXING_WAIT_SECONDS
        
        time.sleep(wait_seconds)

        logger.info(f"Searching for open issues in repository: {self.repo_name}")
        all_issues = self.github_client.get_open_issues(self.repo_name)
        if not all_issues:
            logger.info("No open issues found.")
            return None

        candidate_issues = self._find_candidates_by_role(all_issues, agent_role)
        if not candidate_issues:
            return None

        return self._find_first_assignable_task(candidate_issues, agent_id)
