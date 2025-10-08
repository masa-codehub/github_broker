import asyncio
import json
import logging
import threading
import time
from typing import TYPE_CHECKING

from github import GithubException
from pydantic import HttpUrl
from redis.exceptions import RedisError

from github_broker.domain.task import Task, TaskCandidateStatus
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient
from github_broker.interface.models import TaskResponse, TaskCandidate

if TYPE_CHECKING:
    from github_broker.infrastructure.config import Settings
    from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor

logger = logging.getLogger(__name__)


class TaskService:
    repo_name: str

    def __init__(
        self,
        redis_client: RedisClient,
        github_client: GitHubClient,
        settings: "Settings",
        gemini_executor: "GeminiExecutor",
    ):
        self.redis_client = redis_client
        self.github_client = github_client
        self.settings = settings  # Keep settings object
        self.repo_name = settings.GITHUB_REPOSITORY
        self.github_indexing_wait_seconds = settings.GITHUB_INDEXING_WAIT_SECONDS
        self.polling_interval_seconds = settings.POLLING_INTERVAL_SECONDS
        self.long_polling_check_interval = settings.LONG_POLLING_CHECK_INTERVAL
        self.gemini_executor = gemini_executor

    def create_task_candidate(self, issue_id: int, branch_name: str) -> TaskCandidate:
        task_candidate = TaskCandidate(
            issue_id=issue_id,
            branch_name=branch_name,
            status=TaskCandidateStatus.NEEDS_REVIEW,
        )
        self.redis_client.set_value(
            f"task_candidate:{issue_id}", task_candidate.model_dump_json()
        )
        return task_candidate

    def start_polling(self, stop_event: "threading.Event | None" = None):
        # This method seems fine and doesn't have major conflicts.
        # I will keep the version from HEAD which is the same as main.
        logger.info("Starting issue polling...")
        while not (stop_event and stop_event.is_set()):
            try:
                logger.info(f"Fetching open issues from {self.repo_name}...")
                issues = self.github_client.get_open_issues()
                if issues:
                    logger.info(
                        f"Found {len(issues)} open issues. Caching them in Redis."
                    )
                    self.redis_client.set_value("open_issues", json.dumps(issues))
                    logger.info("Finished caching all open issues under a single key.")
                else:
                    self.redis_client.set_value("open_issues", json.dumps([]))
                    logger.info("No open issues found. Cached an empty list.")

            except (GithubException, RedisError) as e:
                logger.error(f"An error occurred during polling: {e}", exc_info=True)
            except Exception as e:
                logger.error(
                    f"An unexpected error occurred during polling: {e}", exc_info=True
                )

            time.sleep(self.polling_interval_seconds)

        logger.info("Polling stopped.")

    # Use the cleaner implementation from `main`
    def complete_previous_task(self, agent_id: str):
        """
        前タスクの完了処理を行います。
        in-progressとagent_idラベルを持つIssueをGitHub API経由で直接検索し、それらのラベルを削除し、needs-reviewラベルを付与します。
        """
        logger.info("[agent_id=%s] Completing previous task.", agent_id)
        try:
            previous_issues_to_complete = self.github_client.find_issues_by_labels(
                labels=["in-progress", agent_id]
            )
            if not previous_issues_to_complete:
                logger.info(
                    "[agent_id=%s] No in-progress issues found for this agent via GitHub search.",
                    agent_id,
                )
                return

            for issue in previous_issues_to_complete:
                remove_labels = ["in-progress", agent_id]
                add_labels = ["needs-review"]
                try:
                    self.github_client.update_issue(
                        issue_id=issue["number"],
                        remove_labels=remove_labels,
                        add_labels=add_labels,
                    )
                    logger.info(
                        "[issue_id=%s, agent_id=%s] Updated labels: removed %s, added %s.",
                        issue["number"],
                        agent_id,
                        remove_labels,
                        add_labels,
                    )
                except GithubException as e:
                    logger.error(
                        "[issue_id=%s, agent_id=%s] Failed to update issue: %s",
                        issue["number"],
                        agent_id,
                        e,
                        exc_info=True,
                    )
                except Exception as e:
                    logger.error(
                        "[issue_id=%s, agent_id=%s] An unexpected error occurred while updating issue: %s",
                        issue["number"],
                        agent_id,
                        e,
                        exc_info=True,
                    )
        except GithubException as e:
            logger.error(
                "[agent_id=%s] Failed to find issues by labels: %s",
                agent_id,
                e,
                exc_info=True,
            )

    def _find_candidates_by_role(self, issues: list, agent_role: str) -> list:
        # This method is fine.
        """指定された役割（role）ラベルを持つIssueをフィルタリングします。"""
        candidate_issues = []
        for issue in issues:
            labels = {label.get("name") for label in issue.get("labels", [])}
            if (
                agent_role in labels
                and "in-progress" not in labels
            ):
                candidate_issues.append(issue)

        if not candidate_issues:
            logger.info(
                f"[agent_role={agent_role}] No issues found with role label that do not also have 'needs-review'."
            )
        return candidate_issues

    def _find_first_assignable_task(
        self, candidate_issues: list, agent_id: str
    ) -> TaskResponse | None:
        # This method is mostly from HEAD, but I'll ensure the redis logic is correct.
        # The HEAD version seems correct here.
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
                    f"[issue_id={task.issue_id}] Issue is not assignable (missing '成果物' section). Skipping."
                )
                continue

            branch_name = task.extract_branch_name()
            if not branch_name:
                logger.warning(
                    f"[issue_id={task.issue_id}] の本文にブランチ名が見つかりませんでした。このIssueはスキップされます。"
                )
                continue

            lock_key = f"issue_lock_{task.issue_id}"
            if not self.redis_client.acquire_lock(lock_key, agent_id, timeout=600):
                logger.warning(
                    f"[issue_id={task.issue_id}] Issue is locked by another agent. Skipping."
                )
                continue

            try:
                logger.info(
                    f"[issue_id={task.issue_id}, agent_id={agent_id}] Lock acquired for issue. Assigning task."
                )
                self.github_client.add_label(task.issue_id, "in-progress")
                self.github_client.add_label(task.issue_id, agent_id)
                logger.info(
                    f"[issue_id={task.issue_id}, agent_id={agent_id}] Assigned agent to issue."
                )

                self.github_client.create_branch(branch_name)

                prompt = self.gemini_executor.build_prompt(
                    html_url=task.html_url, branch_name=branch_name
                )

                self.redis_client.set_value(
                    f"agent_current_task:{agent_id}", str(task.issue_id), timeout=3600
                )
                logger.info(
                    f"[issue_id={task.issue_id}, agent_id={agent_id}] Stored current task in Redis."
                )

                task_type = "review" if "needs-review" in task.labels else "development"
                return TaskResponse(
                    issue_id=task.issue_id,
                    issue_url=HttpUrl(task.html_url),
                    title=task.title,
                    body=task.body,
                    labels=task.labels,
                    branch_name=branch_name,
                    prompt=prompt,
                    task_type=task_type,
                )
            except Exception as e:
                logger.error(
                    f"[issue_id={task.issue_id}, agent_id={agent_id}] Failed to process issue after acquiring lock: {e}",
                    exc_info=True,
                )
                try:
                    self.github_client.update_issue(
                        issue_id=task.issue_id,
                        remove_labels=["in-progress", agent_id],
                    )
                    logger.info(
                        f"[issue_id={task.issue_id}, agent_id={agent_id}] Rolled back labels."
                    )
                except Exception as rollback_e:
                    logger.error(
                        f"[issue_id={task.issue_id}, agent_id={agent_id}] Failed to rollback labels: {rollback_e}",
                        exc_info=True,
                    )
                finally:
                    self.redis_client.release_lock(lock_key)
                    logger.info(
                        f"[issue_id={task.issue_id}, agent_id={agent_id}] Released lock."
                    )
                raise

        logger.info(f"[agent_id={agent_id}] No assignable and unlocked issues found.")
        return None

    # This is the core of the PR, keep the HEAD version.
    async def request_task(
        self, agent_id: str, agent_role: str, timeout: int | None = 120
    ) -> TaskResponse | None:
        """
        エージェントの役割（role）に基づいて最適なIssueを探し、タスク情報を返します。
        利用可能なタスクがない場合、指定されたタイムアウト時間までタスクの出現を待ち続けます（ロングポーリング）。
        """
        start_time = time.monotonic()
        check_interval = self.long_polling_check_interval

        task = await self._check_for_available_task(
            agent_id, agent_role, is_first_check=True
        )
        if task:
            return task

        if timeout is None:
            logger.info("No timeout specified, returning immediately.")
            return None

        logger.info(
            f"No task found initially. Starting long polling for {timeout} seconds..."
        )

        while True:
            elapsed_time = time.monotonic() - start_time

            if elapsed_time >= timeout:
                logger.info(
                    f"Long polling timeout ({timeout}s) reached. No task found."
                )
                return None

            remaining_time = timeout - elapsed_time
            wait_time = min(check_interval, remaining_time)

            logger.debug(
                f"Waiting {wait_time}s before next check (elapsed: {elapsed_time:.1f}s)"
            )
            await asyncio.sleep(wait_time)

            task = await self._check_for_available_task(
                agent_id, agent_role, is_first_check=False
            )
            if task:
                logger.info(f"Task found during long polling after {elapsed_time:.1f}s")
                return task

    # This is also core to the PR, keep the HEAD version, but fix the call to complete_previous_task
    async def _check_for_available_task(
        self, agent_id: str, agent_role: str, is_first_check: bool = True
    ) -> TaskResponse | None:
        """
        利用可能なタスクをチェックして返します。ロングポーリング用のヘルパーメソッド。

        Args:
            agent_id (str): タスクを要求するエージェントのID。
            agent_role (str): エージェントの役割。
            is_first_check (bool): 最初のチェックかどうか。最初のチェック時のみ前回タスクの完了処理を行います。

        Returns:
            TaskResponse | None: 見つかったタスクの情報。見つからなかった場合はNoneを返します。
        """
        cached_issues_json = self.redis_client.get_value("open_issues")

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

        if is_first_check:
            self.complete_previous_task(agent_id)  # Corrected call

        candidate_issues = self._find_candidates_by_role(all_issues, agent_role)
        if candidate_issues:
            logger.debug(
                f"Found {len(candidate_issues)} candidate issues for role '{agent_role}'."
            )
            task = self._find_first_assignable_task(candidate_issues, agent_id)
            if task:
                return task
        else:
            logger.debug(
                f"No candidate issues found for role '{agent_role}' in cached issues."
            )

        return None
