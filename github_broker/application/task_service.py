from __future__ import annotations

import json
import logging
import threading
import time
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from github import GithubException
from pydantic import HttpUrl
from redis.exceptions import RedisError

from github_broker.domain.agent_config import AgentConfigList
from github_broker.domain.task import Task
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient
from github_broker.interface.models import TaskCandidate, TaskResponse, TaskType

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)


class TaskService:
    # Priority constants
    PRIORITY_HIGH_LABEL = "priority:high"
    PRIORITY_MEDIUM_LABEL = "priority:medium"
    PRIORITY_LOW_LABEL = "priority:low"
    PRIORITY_HIGH_VALUE = 3
    PRIORITY_MEDIUM_VALUE = 2
    PRIORITY_LOW_VALUE = 1
    PRIORITY_DEFAULT_VALUE = 0

    # Label constants
    LABEL_NEEDS_REVIEW = "needs-review"
    LABEL_REVIEW_DONE = "review-done"
    LABEL_IN_PROGRESS = "in-progress"

    # Review constants
    REVIEW_ISSUE_TIMESTAMP_KEY_FORMAT = "review_issue_detected_timestamp:{issue_id}"
    REVIEW_ASSIGNMENT_DELAY_MINUTES = 5
    REVIEW_TIMEOUT_MINUTES = 10  # Assuming this value, was on settings
    POLLING_INTERVAL_SECONDS = 5 * 60  # Assuming this value, was on settings

    def __init__(
        self,
        github_client: GitHubClient,
        redis_client: RedisClient,
        agent_configs: AgentConfigList,
    ):
        self.github_client = github_client
        self.redis_client = redis_client
        self.agent_roles = {agent.role for agent in agent_configs.get_all()}
        self.repo_name = self.github_client._repo_name

    def start_polling(self, stop_event: threading.Event | None = None):
        logger.info("Starting issue polling...")
        while not (stop_event and stop_event.is_set()):
            try:
                logger.info(f"Fetching open issues from {self.repo_name}...")
                issues = self.github_client.get_open_issues()
                self.redis_client.sync_issues(issues)

                # レビューIssueの検索とタイムスタンプの保存
                self._find_review_task()

            except (GithubException, RedisError) as e:
                logger.error(
                    f"An error occurred during issue polling: {e}", exc_info=True
                )
            except Exception as e:
                logger.error(
                    f"An unexpected error occurred during issue polling: {e}",
                    exc_info=True,
                )

            try:
                self.poll_and_process_reviews()
            except (GithubException, RedisError) as e:
                logger.error(
                    f"An error occurred during review polling: {e}", exc_info=True
                )
            except Exception as e:
                logger.error(
                    f"An unexpected error occurred during review polling: {e}",
                    exc_info=True,
                )

            time.sleep(self.POLLING_INTERVAL_SECONDS)

        logger.info("Polling stopped.")

    def get_highest_priority_label(self, all_labels: list[str]) -> str | None:
        """
        与えられたラベルのリストから最も高い優先度ラベルを特定します。

        Args:
            all_labels (list[str]): すべてのIssueから集めたラベルのリスト。

        Returns:
            str | None: 最も高い優先度ラベル (例: 'P0')。優先度ラベルがない場合はNone。
        """
        logger.info("Determining the highest priority label from the provided list of all labels...")
        highest_priority = self._determine_highest_priority(all_labels)
        if highest_priority:
            logger.info(f"Highest priority label found: {highest_priority}")
        else:
            logger.info("No priority labels found among the provided labels.")
        return highest_priority

    def _find_review_task(self) -> None:
        """
        レビュー待ちのIssueを検索し、Redisにタイムスタンプを保存します。
        """
        logger.info("Searching for review issues...")
        try:
            review_issues = self.github_client.get_review_issues()
            for issue in review_issues:
                issue_id = issue.get("number")
                if issue_id:
                    timestamp_key = self.REVIEW_ISSUE_TIMESTAMP_KEY_FORMAT.format(
                        issue_id=issue_id
                    )
                    # Redisに存在しない場合のみタイムスタンプを保存
                    if not self.redis_client.get_value(timestamp_key):
                        self.redis_client.set_value(
                            timestamp_key, datetime.now(UTC).isoformat()
                        )
                        logger.info(
                            f"[issue_id={issue_id}] Detected review issue and stored timestamp in Redis."
                        )
        except GithubException as e:
            logger.error(
                f"An error occurred while searching for review issues: {e}",
                exc_info=True,
            )

    def poll_and_process_reviews(self):
        """
        'needs-review'ラベルが付いたIssueをポーリングし、関連するPRがタイムアウトした場合に
        'review-done'ラベルを付与します。
        """
        logger.info("Polling for pull requests needing review...")
        try:
            # 修正: IssueごとのAPIコールを避けるため、一括でPR情報を取得
            pr_map = self.github_client.get_needs_review_issues_and_prs()
            logger.info(f"Found {len(pr_map)} pull requests in review.")

            for pr_number, pr in pr_map.items():
                logger.debug(f"[pr_number={pr_number}] Processing PR in review.")

                timeout_minutes = self.REVIEW_TIMEOUT_MINUTES
                timeout_delta = timedelta(minutes=timeout_minutes)
                pr_created_at = pr.created_at
                if pr_created_at.tzinfo is None:
                    pr_created_at = pr_created_at.replace(tzinfo=UTC)
                else:
                    pr_created_at = pr_created_at.astimezone(UTC)
                time_since_creation = datetime.now(UTC) - pr_created_at

                if time_since_creation > timeout_delta:
                    logger.info(
                        f"[pr_number={pr_number}] PR has exceeded the review timeout of {timeout_minutes} minutes. Adding 'review-done' label."
                    )
                    try:
                        self.github_client.add_label_to_pr(
                            pr_number=pr_number, label=self.LABEL_REVIEW_DONE
                        )
                        logger.info(
                            f"[pr_number={pr_number}] Successfully added 'review-done' label."
                        )
                    except GithubException as e:
                        logger.error(
                            f"[pr_number={pr_number}] Failed to add 'review-done' label: {e}",
                            exc_info=True,
                        )
                else:
                    logger.debug(
                        f"[pr_number={pr_number}] PR is within the review timeout. Skipping."
                    )

        except GithubException as e:
            logger.error(f"An error occurred during review polling: {e}", exc_info=True)
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during review polling: {e}",
                exc_info=True,
            )

    def complete_previous_task(self, agent_id: str):
        logger.info("[agent_id=%s] Completing previous task.", agent_id)
        try:
            previous_issues_to_complete = self.github_client.find_issues_by_labels(
                labels=[self.LABEL_IN_PROGRESS, agent_id]
            )
            if not previous_issues_to_complete:
                logger.info(
                    "[agent_id=%s] No in-progress issues found for this agent via GitHub search.",
                    agent_id,
                )
                return

            for issue in previous_issues_to_complete:
                remove_labels = [self.LABEL_IN_PROGRESS, agent_id]
                add_labels = [self.LABEL_NEEDS_REVIEW]
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

    @staticmethod
    def _get_priority_from_label(label_name: str) -> int | None:
        if label_name.startswith("P") and label_name[1:].isdigit():
            return int(label_name[1:])
        return None

    def _has_priority_label(self, labels: set[str]) -> bool:
        return any(self._get_priority_from_label(name) is not None for name in labels)

    def _determine_highest_priority(self, labels: list[str]) -> str | None:
        """
        優先度ラベルのリストから最も高い優先度（数字が最小）を特定します。

        Args:
            labels (list[str]): Issueに付与されているラベル名のリスト。

        Returns:
            str | None: 最も高い優先度ラベル (例: 'P0')。優先度ラベルがない場合はNone。
        """
        priority_tuples = [
            (self._get_priority_from_label(label), label)
            for label in labels
            if self._get_priority_from_label(label) is not None
        ]

        if priority_tuples:
            # self._get_priority_from_labelがNoneでないことを確認済みなので、
            # mypyのためのキャストを追加
            valid_priority_tuples: list[tuple[int, str]] = [
                (p, label) for p, label in priority_tuples if p is not None
            ]
            return min(valid_priority_tuples)[1]
        return None

    def _find_candidates_for_any_role(
        self, issues: list[dict[str, Any]], highest_priority: str | None
    ) -> list[dict[str, Any]]:
        candidate_issues = []
        for issue in issues:
            label_names = (label.get("name") for label in issue.get("labels", []))
            labels = {name for name in label_names if name is not None}

            # 優先度ラベルのフィルタリング
            if highest_priority and highest_priority not in labels:
                continue

            # 役割ラベルが付いているかチェック
            role_labels = labels.intersection(self.agent_roles)
            if not role_labels:
                continue  # 役割ラベルがないIssueはスキップ

            is_development_candidate = (
                self.LABEL_IN_PROGRESS not in labels
                and self.LABEL_NEEDS_REVIEW not in labels
                and not {"story", "epic"}.intersection(labels)
                and self._has_priority_label(labels)
            )
            is_review_candidate = (
                self.LABEL_IN_PROGRESS not in labels
                and self.LABEL_NEEDS_REVIEW in labels
                and not {"story", "epic"}.intersection(labels)
            )

            if is_development_candidate:
                candidate_issues.append(issue)
            elif is_review_candidate:
                issue_id = issue.get("number")
                if issue_id is None:
                    logger.warning(
                        f"Issue with missing number found: {issue}. Skipping."
                    )
                    continue

                # Redisに保存されたタイムスタンプを確認
                timestamp_key = self.REVIEW_ISSUE_TIMESTAMP_KEY_FORMAT.format(
                    issue_id=issue_id
                )
                detected_timestamp_str = self.redis_client.get_value(timestamp_key)

                if detected_timestamp_str:
                    detected_timestamp = datetime.fromisoformat(detected_timestamp_str)
                    if detected_timestamp.tzinfo is None:
                        detected_timestamp = detected_timestamp.replace(tzinfo=UTC)
                    else:
                        detected_timestamp = detected_timestamp.astimezone(UTC)
                    time_since_detection = datetime.now(UTC) - detected_timestamp
                    if time_since_detection >= timedelta(
                        minutes=self.REVIEW_ASSIGNMENT_DELAY_MINUTES
                    ):
                        logger.info(
                            f"[issue_id={issue_id}] Review issue detected more than {self.REVIEW_ASSIGNMENT_DELAY_MINUTES} minutes ago. Adding to candidates."
                        )
                        candidate_issues.append(issue)
                    else:
                        logger.info(
                            f"[issue_id={issue_id}] Review issue detected less than {self.REVIEW_ASSIGNMENT_DELAY_MINUTES} minutes ago. Skipping for now."
                        )
                else:
                    logger.info(
                        f"[issue_id={issue_id}] Review issue has no detection timestamp in Redis. Skipping."
                    )

        if not candidate_issues:
            logger.info("No assignable issues found with a role label.")
        return candidate_issues

    @staticmethod
    def _sort_issues_by_priority(issues: list[dict]) -> list[dict]:
        """
        Issueのリストを優先度ラベルに基づいてソートします。
        P0 > P1 > P2 の順に優先度が高く、優先度ラベルがないIssueは末尾に配置されます。

        Args:
            issues (list[dict]): ソート対象のIssueのリスト。

        Returns:
            list[dict]: 優先度に基づいてソートされたIssueのリスト。
        """

        def get_priority_key(issue: dict) -> int | float:
            """Extracts the lowest priority number from an issue's labels."""
            label_names = (label.get("name", "") for label in issue.get("labels", []))
            priority_numbers = (
                int(name[1:])
                for name in label_names
                if name.startswith("P") and name[1:].isdigit()
            )
            return min(priority_numbers, default=float("inf"))

        return sorted(issues, key=get_priority_key)

    async def _find_first_assignable_task(
        self, candidate_issues: list, agent_id: str
    ) -> TaskResponse | None:
        assert self.repo_name is not None
        sorted_issues = self._sort_issues_by_priority(candidate_issues)
        logger.info(
            "候補Issueを優先度順にソートしました: %s",
            [issue["number"] for issue in sorted_issues],
        )
        for issue_obj in sorted_issues:
            task = Task(
                issue_id=issue_obj["number"],
                title=issue_obj["title"],
                body=issue_obj["body"] or "",
                html_url=issue_obj["html_url"],
                labels=[label["name"] for label in issue_obj.get("labels", [])],
            )

            if not task.is_assignable():
                logger.info(
                    "[issue_id=%s] Issueは割り当て不可能です（'成果物'セクションがありません）。スキップします。",
                    task.issue_id,
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
                self.github_client.add_label(task.issue_id, self.LABEL_IN_PROGRESS)
                self.github_client.add_label(task.issue_id, agent_id)
                logger.info(
                    f"[issue_id={task.issue_id}, agent_id={agent_id}] Assigned agent to issue."
                )

                self.github_client.create_branch(branch_name)

                # NOTE: GeminiExecutor logic is removed as part of the merge.
                # This needs to be handled by the new architecture.
                prompt = "PROMPT_GENERATION_LOGIC_REMOVED"
                gemini_response = "GEMINI_EXECUTION_LOGIC_REMOVED"


                self.redis_client.set_value(
                    f"agent_current_task:{agent_id}",
                    str(task.issue_id),
                    timeout=3600,
                )
                logger.info(
                    f"[issue_id={task.issue_id}, agent_id={agent_id}] Stored current task in Redis."
                )

                # 役割ラベルを抽出
                role_labels = [
                    label for label in task.labels if label in self.agent_roles
                ]

                assert (
                    role_labels
                ), f"Candidate issue {task.issue_id} must have at least one role label."

                if len(role_labels) > 1:
                    logger.warning(
                        f"[issue_id={task.issue_id}] Multiple role labels found: {role_labels}. "
                        f"Using the first one: {role_labels[0]}"
                    )

                required_role = role_labels[0]

                task_type = (
                    TaskType.REVIEW
                    if self.LABEL_NEEDS_REVIEW in task.labels
                    else TaskType.DEVELOPMENT
                )
                return TaskResponse(
                    issue_id=task.issue_id,
                    issue_url=HttpUrl(task.html_url),
                    title=task.title,
                    body=task.body,
                    labels=task.labels,
                    branch_name=branch_name,
                    prompt=prompt,
                    required_role=required_role,
                    task_type=task_type,
                    gemini_response=gemini_response,
                )
            except Exception as e:
                logger.error(
                    f"[issue_id={task.issue_id}, agent_id={agent_id}] Failed to process issue after acquiring lock: {e}",
                    exc_info=True,
                )
                try:
                    self.github_client.update_issue(
                        issue_id=task.issue_id,
                        remove_labels=[self.LABEL_IN_PROGRESS, agent_id],
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

    async def request_task(self, agent_id: str) -> TaskResponse | None:
        logger.info("タスクをリクエストしています: agent_id=%s", agent_id)
        return await self._check_for_available_task(agent_id, is_first_check=True)

    async def _check_for_available_task(
        self, agent_id: str, is_first_check: bool = True
    ) -> TaskResponse | None:
        if is_first_check:
            self.complete_previous_task(agent_id)

        issue_keys = self.redis_client.get_keys_by_pattern("issue:*")
        if not issue_keys:
            logger.warning("No issues found in Redis cache.")
            return None

        cached_issues_json = self.redis_client.get_values(issue_keys)
        try:
            all_issues = [
                json.loads(issue_json)
                for issue_json in cached_issues_json
                if issue_json is not None
            ]
        except json.JSONDecodeError:
            logger.error(
                "Failed to decode issues from Redis cache. The cache might be corrupted.",
                exc_info=True,
            )
            return None

        all_labels = [
            label["name"]
            for issue in all_issues
            for label in issue.get("labels", [])
        ]
        highest_priority_label = self.get_highest_priority_label(all_labels)

        if not highest_priority_label:
            logger.info("オープンなIssueに優先度ラベルが見つかりませんでした。割り当てるタスクはありません。")
            return None

        candidate_issues = self._find_candidates_for_any_role(
            all_issues, highest_priority_label
        )

        if candidate_issues:
            logger.info(
                "最高優先度ラベル '%s' を持つタスク候補が %d 件見つかりました。",
                highest_priority_label,
                len(candidate_issues),
            )
            task = await self._find_first_assignable_task(candidate_issues, agent_id)
            if task:
                return task
        else:
            logger.info(
                "最高優先度ラベル '%s' を持つ割り当て可能なタスク候補は見つかりませんでした。",
                highest_priority_label,
            )

        return None

    def create_task_candidate(self, issue_id: int, agent_id: str):
        """TaskCandidateを作成し、Redisに保存します。"""
        task_candidate = TaskCandidate(issue_id=issue_id, agent_id=agent_id)
        self.redis_client.set_value(
            f"task_candidate:{issue_id}:{agent_id}",
            task_candidate.model_dump_json(),
            timeout=86400,
        )
        logger.info(
            f"[issue_id={issue_id}, agent_id={agent_id}] Created task candidate with status {task_candidate.status.value}."
        )

    async def create_fix_task(
        self, pull_request_number: int, review_comments: list[str]
    ):
        """レビューコメントに基づいて修正タスクを生成し、Redisに保存します。"""
        logger.info(f"Creating fix task for PR #{pull_request_number}...")

        # 1. Issue情報を取得し、役割ラベルを抽出
        issue_data = self.github_client.get_issue_by_number(pull_request_number)
        issue_labels = {label["name"] for label in issue_data.get("labels", [])}
        role_labels = list(issue_labels.intersection(self.agent_roles))

        # 2. 修正タスクのラベルを構築
        fix_labels = ["fix"] + role_labels

        pr_url = f"https://github.com/{self.repo_name}/pull/{pull_request_number}"

        # NOTE: GeminiExecutor logic is removed as part of the merge.
        # This needs to be handled by the new architecture.
        prompt = "PROMPT_GENERATION_LOGIC_REMOVED"

        task_data = {
            "issue_id": pull_request_number,
            "title": f"Fix task for PR #{pull_request_number}",
            "body": prompt,
            "html_url": pr_url,
            "labels": fix_labels,
            "task_type": TaskType.FIX.value,
        }

        redis_key = f"task:fix:{pull_request_number}"
        self.redis_client.set_value(
            redis_key,
            json.dumps(task_data),
            timeout=86400,
        )

        logger.info(
            f"Successfully created and stored fix task for PR #{pull_request_number} in Redis key: {redis_key}"
        )
