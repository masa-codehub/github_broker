import json
import logging
import threading
import time
from typing import TYPE_CHECKING

from github import GithubException
from pydantic import HttpUrl
from redis.exceptions import RedisError

from github_broker.domain.task import Task
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient
from github_broker.interface.models import TaskResponse

if TYPE_CHECKING:
    from github_broker.infrastructure.config import Settings

logger = logging.getLogger(__name__)

# --- Constants ---
_DEFAULT_GITHUB_INDEXING_WAIT_SECONDS = 15
OPEN_ISSUES_CACHE_KEY = "open_issues"


class TaskService:
    repo_name: str

    def __init__(
        self,
        redis_client: RedisClient,
        github_client: GitHubClient,
        settings: "Settings",
    ):
        self.redis_client = redis_client
        self.github_client = github_client
        self.repo_name = settings.GITHUB_REPOSITORY
        self.github_indexing_wait_seconds = settings.GITHUB_INDEXING_WAIT_SECONDS
        self.polling_interval_seconds = settings.POLLING_INTERVAL_SECONDS

    def start_polling(self, stop_event: "threading.Event | None" = None):
        """
        GitHubリポジトリから定期的にオープンなIssueを取得し、Redisにキャッシュします。
        stop_eventがセットされるまでポーリングを続けます。
        """
        logger.info("Starting issue polling...")
        while not (stop_event and stop_event.is_set()):
            try:
                logger.info(f"Fetching open issues from {self.repo_name}...")
                issues = self.github_client.get_open_issues()
                if issues:
                    logger.info(
                        f"Found {len(issues)} open issues. Caching them in Redis."
                    )
                    self.redis_client.set_value(
                        OPEN_ISSUES_CACHE_KEY, json.dumps(issues)
                    )
                    logger.info("Finished caching all open issues under a single key.")
                else:
                    # Issueが0件の場合も空のリストをキャッシュに保存することで、
                    # クローズされたIssueがキャッシュに残り続けるのを防ぐ
                    self.redis_client.set_value(OPEN_ISSUES_CACHE_KEY, json.dumps([]))
                    logger.info("No open issues found. Cached an empty list.")

            except (GithubException, RedisError) as e:
                logger.error(f"An error occurred during polling: {e}", exc_info=True)
            except Exception as e:
                logger.error(
                    f"An unexpected error occurred during polling: {e}", exc_info=True
                )

            time.sleep(self.polling_interval_seconds)

        logger.info("Polling stopped.")

    def complete_previous_task(self, agent_id: str, all_issues: list[dict]):
        """
        前タスクの完了処理を行います。
        in-progressとagent_idラベルを持つIssueを検索し、それらのラベルを削除し、needs-reviewラベルを付与します。
        """
        logger.info(f"Completing previous task for agent: {agent_id}")

        previous_issues = []
        for issue in all_issues:
            labels = {label.get("name") for label in issue.get("labels", [])}
            if "in-progress" in labels and agent_id in labels:
                previous_issues.append(issue)
        if not previous_issues:
            logger.info("No in-progress issues found for this agent.")
            return

        for issue in previous_issues:
            logger.info(
                f"Found previous in-progress issue #{issue['number']} for agent {agent_id}."
            )
            remove_labels = ["in-progress", agent_id]
            add_labels = ["needs-review"]

            try:
                self.github_client.update_issue(
                    issue_id=issue["number"],
                    remove_labels=remove_labels,
                    add_labels=add_labels,
                )
                logger.info(
                    f"Updated labels for issue #{issue["number"]}: removed {remove_labels}, added {add_labels}."
                )
            except GithubException as e:
                logger.error(
                    f"Failed to update issue #{issue["number"]} for agent {agent_id}: {e}",
                    exc_info=True,
                )
                # エラーが発生してもループを中断せず、次のIssueの処理に進む
            except Exception as e:
                logger.error(
                    f"An unexpected error occurred while updating issue #{issue["number"]} for agent {agent_id}: {e}",
                    exc_info=True,
                )
                # 予期せぬエラーが発生してもループを中断せず、次のIssueの処理に進む

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
                self.github_client.add_label(task.issue_id, "in-progress")
                self.github_client.add_label(task.issue_id, agent_id)
                logger.info(f"Assigned agent '{agent_id}' to issue #{task.issue_id}.")

                self.github_client.create_branch(branch_name)

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

    def request_task(self, agent_id: str, agent_role: str) -> TaskResponse | None:
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
        cached_issues_json = self.redis_client.get_value(OPEN_ISSUES_CACHE_KEY)

        if not cached_issues_json:
            logger.warning("No issues found in Redis cache.")
            return None

        try:
            all_issues = json.loads(cached_issues_json)
        except json.JSONDecodeError:
            logger.error(
                "Failed to decode issues from Redis cache. The cache might be corrupted.",
                exc_info=True,
            )
            return None
        self.complete_previous_task(agent_id, all_issues)

        candidate_issues = self._find_candidates_by_role(all_issues, agent_role)
        if candidate_issues:
            logger.info(
                f"Found {len(candidate_issues)} candidate issues for role '{agent_role}'."
            )
            task = self._find_first_assignable_task(candidate_issues, agent_id)
            if task:
                return task
        else:
            logger.info(
                f"No candidate issues found for role '{agent_role}' in cached issues."
            )

        logger.info("No assignable task found from cached issues.")
        return None
