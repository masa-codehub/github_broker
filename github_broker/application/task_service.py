import logging
import os
import time

from pydantic import HttpUrl

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
        assert self.repo_name is not None
        logger.info(f"Completing previous task for agent: {agent_id}")
        all_issues = self.redis_client.get_all_issues()
        if not all_issues:
            logger.info("No issues found in Redis cache.")
            return

        previous_issues = []
        for issue in all_issues:
            labels = [label["name"] for label in issue.get("labels", [])]
            if "in-progress" in labels and agent_id in labels:
                previous_issues.append(issue)

        for issue in previous_issues:
            logger.info(
                f"Found previous in-progress issue #{issue['number']} for agent {agent_id}."
            )
            remove_labels = ["in-progress", agent_id]
            add_labels = ["needs-review"]

            self.github_client.update_issue(
                repo_name=self.repo_name,
                issue_id=issue["number"],
                remove_labels=remove_labels,
                add_labels=add_labels,
            )
            logger.info(
                f"Updated labels for issue #{issue['number']}: removed {remove_labels}, added {add_labels}."
            )

    def _find_candidates_by_role(self, issues: list, agent_role: str) -> list:
        """指定された役割（role）ラベルを持つIssueをフィルタリングします。"""
        candidate_issues = []
        for issue in issues:
            labels = {label.get("name") for label in issue.get("labels", [])}
            if agent_role in labels and "needs-review" not in labels:
                candidate_issues.append(issue)

        if not candidate_issues:
            logger.info(
                f"No issues found with role label '{agent_role}' that do not also have 'needs-review'."
            )
        return candidate_issues

    def _find_first_assignable_task(
        self, candidate_issues: list, agent_id: str
    ) -> TaskResponse | None:
        """候補リストから、最初に割り当て可能なタスクを見つけます。"""
        assert self.repo_name is not None
        for issue_obj in sorted(candidate_issues, key=lambda i: i.get("number", 0)):
            task = Task(
                issue_id=issue_obj["number"],
                title=issue_obj["title"],
                body=issue_obj["body"] or "",
                html_url=issue_obj["html_url"],
                labels=[label["name"] for label in issue_obj.get("labels", [])],
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
                    issue_url=HttpUrl(task.html_url),
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
        self, agent_id: str, agent_role: str, timeout: int | None = 120
    ) -> TaskResponse | None:
        """
        エージェントの役割（role）に基づいて最適なIssueを探し、タスク情報を返します。
        利用可能なタスクがない場合、指定されたタイムアウト時間までタスクの出現を待ち続けます（ロングポーリング）。

        Args:
            agent_id (str): タスクを要求するエージェントのID。
            agent_role (str): エージェントの役割。
            timeout (int | None): ロングポーリングのタイムアウト時間（秒）。Noneの場合、待機せずに即時リターンします。
                                  デフォルトは120秒です。

        Returns:
            TaskResponse | None: 見つかったタスクの情報。タイムアウトした場合はNoneを返します。
        """
        self.complete_previous_task(agent_id)

        try:
            wait_seconds = int(
                os.getenv(
                    _GITHUB_INDEXING_WAIT_SECONDS_ENV,
                    _DEFAULT_GITHUB_INDEXING_WAIT_SECONDS,
                )
            )
        except ValueError:
            wait_seconds = _DEFAULT_GITHUB_INDEXING_WAIT_SECONDS
            logger.warning(
                f"Invalid value for {_GITHUB_INDEXING_WAIT_SECONDS_ENV}. "
                f"Falling back to default {wait_seconds} seconds."
            )
        time.sleep(wait_seconds)

        polling_timeout = timeout if timeout is not None else 0
        end_time = time.time() + polling_timeout

        while True:
            logger.info(f"Searching for open issues in repository: {self.repo_name}")
            all_issues = self.redis_client.get_all_issues()
            if all_issues:
                candidate_issues = self._find_candidates_by_role(all_issues, agent_role)
                if candidate_issues:
                    task = self._find_first_assignable_task(candidate_issues, agent_id)
                    if task:
                        return task  # Task found, return immediately

            if time.time() >= end_time:
                break  # Timeout reached

            sleep_interval = 5
            logger.info(
                f"No assignable task found. Retrying in {sleep_interval} seconds..."
            )
            time.sleep(sleep_interval)

        logger.info("Timeout reached. No assignable task found.")
        return None
