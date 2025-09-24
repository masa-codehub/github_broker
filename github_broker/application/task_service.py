import logging
import threading
import time
from typing import TYPE_CHECKING, Any

from github import GithubException
from pydantic import HttpUrl

from github_broker.domain.task import Task
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.interface.models import TaskResponse

if TYPE_CHECKING:
    from github_broker.infrastructure.config import Settings
    from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor

logger = logging.getLogger(__name__)


class TaskService:
    repo_name: str

    def __init__(
        self,
        github_client: GitHubClient,
        settings: "Settings",
        gemini_executor: "GeminiExecutor",
    ):
        self.github_client = github_client
        self.repo_name = settings.GITHUB_REPOSITORY
        self.github_indexing_wait_seconds = settings.GITHUB_INDEXING_WAIT_SECONDS
        self.polling_interval_seconds = settings.POLLING_INTERVAL_SECONDS
        self.gemini_executor = gemini_executor

    def complete_previous_task(self, agent_id: str):
        """
        前タスクの完了処理を行います。
        in-progressとagent_idラベルを持つIssueを検索し、それらのラベルを削除し、needs-reviewラベルを付与します。
        """
        logger.info(f"[agent_id={agent_id}] Completing previous task.")

        previous_issues_to_complete = self.github_client.find_issues_by_labels(
            labels=["in-progress", agent_id]
        )

        if not previous_issues_to_complete:
            logger.info(f"[agent_id={agent_id}] No in-progress issues found for this agent via GitHub search.")
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
                    f"[issue_id={issue['number']}, agent_id={agent_id}] Updated labels: removed {remove_labels}, added {add_labels}."
                )
            except GithubException as e:
                logger.error(
                    f"[issue_id={issue['number']}, agent_id={agent_id}] Failed to update issue: {e}",
                    exc_info=True,
                )
            except Exception as e:
                logger.error(
                    f"[issue_id={issue['number']}, agent_id={agent_id}] An unexpected error occurred while updating issue: {e}",
                    exc_info=True,
                )

    def _find_candidates_by_role(self, issues: list, agent_role: str) -> list:
        """指定された役割（role）ラベルを持つIssueをフィルタリングします。"""
        candidate_issues = []
        for issue in issues:
            labels = {label.get("name") for label in issue.get("labels", [])}
            if (
                agent_role in labels
                and "needs-review" not in labels
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
                    f"[issue_id={task.issue_id}] Issue is not assignable (missing '成果物' section). Skipping."
                )
                continue

            branch_name = task.extract_branch_name()
            if not branch_name:
                logger.warning(
                    f"[issue_id={task.issue_id}] の本文にブランチ名が見つかりませんでした。このIssueはスキップされます。"
                )
                continue

            if "locked" in task.labels:
                logger.warning(
                    f"[issue_id={task.issue_id}] Issue is locked by another agent. Skipping."
                )
                continue

            try:
                logger.info(
                    f"[issue_id={task.issue_id}, agent_id={agent_id}] Attempting to acquire lock for issue via GitHub label."
                )
                self.github_client.add_label(task.issue_id, "locked")
                logger.info(
                    f"[issue_id={task.issue_id}, agent_id={agent_id}] Lock acquired for issue. Assigning task."
                )
                self.github_client.add_label(task.issue_id, "in-progress")
                self.github_client.add_label(task.issue_id, agent_id)
                logger.info(f"[issue_id={task.issue_id}, agent_id={agent_id}] Assigned agent to issue.")

                self.github_client.create_branch(branch_name)

                prompt = self.gemini_executor.build_prompt(
                    issue_id=task.issue_id,
                    title=task.title,
                    body=task.body,
                    branch_name=branch_name,
                )

                return TaskResponse(
                    issue_id=task.issue_id,
                    issue_url=HttpUrl(task.html_url),
                    title=task.title,
                    body=task.body,
                    labels=task.labels,
                    branch_name=branch_name,
                    prompt=prompt,
                )
            except Exception as e:
                logger.error(
                    f"[issue_id={task.issue_id}, agent_id={agent_id}] Failed to process issue after acquiring lock: {e}",
                    exc_info=True,
                )
                try:
                    self.github_client.update_issue(
                        issue_id=task.issue_id,
                        remove_labels=["in-progress", agent_id, "locked"],
                    )
                    logger.info(
                        f"[issue_id={task.issue_id}, agent_id={agent_id}] Rolled back labels: removed 'in-progress', '{agent_id}' and 'locked'."
                    )
                except Exception as rollback_e:
                    logger.error(
                        f"[issue_id={task.issue_id}, agent_id={agent_id}] Failed to rollback labels: {rollback_e}",
                        exc_info=True,
                    )
                raise

        logger.info(f"[agent_id={agent_id}] No assignable and unlocked issues found.")
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

        start_time = time.time()
        while True:
            all_issues = self.github_client.get_open_issues()
            if not all_issues:
                logger.warning(f"[agent_id={agent_id}, agent_role={agent_role}] No open issues found from GitHub.")
            else:
                candidate_issues = self._find_candidates_by_role(all_issues, agent_role)
                if candidate_issues:
                    logger.info(
                        f"[agent_id={agent_id}, agent_role={agent_role}] Found {len(candidate_issues)} candidate issues."
                    )
                    task = self._find_first_assignable_task(candidate_issues, agent_id)
                    if task:
                        logger.info(
                            f"[issue_id={task.issue_id}, agent_id={agent_id}] Assigned current task issue."
                        )
                        return task
                else:
                    logger.info(
                        f"[agent_id={agent_id}, agent_role={agent_role}] No candidate issues found in GitHub issues."
                    )

            if timeout is not None and (time.time() - start_time) > timeout:
                logger.info(f"[agent_id={agent_id}, agent_role={agent_role}] No assignable task found from GitHub issues after polling.")
                return None

            logger.info(
                f"[agent_id={agent_id}, agent_role={agent_role}] No assignable task found. Waiting for {self.polling_interval_seconds} seconds before re-polling."
            )
            time.sleep(self.polling_interval_seconds)
