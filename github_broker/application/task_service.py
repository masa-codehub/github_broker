import logging
import os
import time

from github_broker.domain.task import Task
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient
from github_broker.interface.models import TaskResponse

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, redis_client: RedisClient, github_client: GitHubClient):
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
        previous_issues = self.github_client.search_issues(
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

    def request_task(self, agent_id: str) -> TaskResponse | None:
        """
        GitHubからアサイン可能なIssueを探し、ロックして、タスク情報を返します。
        アサイン可能なIssueとは、オープンであり、かつ本文にブランチ名が指定されているものです。
        """
        self.complete_previous_task(agent_id)
        # GitHubの検索インデックス遅延を考慮し、一定時間待機
        time.sleep(15)
        logger.info(f"Searching for open issues in repository: {self.repo_name}")
        github_issues = self.github_client.get_open_issues(self.repo_name)

        if not github_issues:
            logger.info("No open issues found.")
            return None

        for issue in github_issues:
            task = Task(
                issue_id=issue.number,
                title=issue.title,
                body=issue.body or "",
                html_url=issue.html_url,
                labels=[label.name for label in issue.labels],
            )
            branch_name = task.extract_branch_name()

            if not branch_name:
                logger.warning(
                    f"Issue #{task.issue_id} の本文にブランチ名が見つかりませんでした。このIssueはスキップされます。"
                )
                continue

            lock_key = f"issue_lock_{task.issue_id}"
            logger.info(f"Attempting to acquire lock for issue #{task.issue_id}")
            if not self.redis_client.acquire_lock(lock_key, "locked", timeout=600):
                logger.warning(
                    f"Issue #{task.issue_id} のロック取得に失敗しました。他のエージェントによってロックされている可能性があります。スキップします。"
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
                    body=task.body or "",
                    labels=task.labels,
                    branch_name=branch_name,
                )
            except Exception as e:
                logger.error(
                    f"ロック取得後にIssue #{task.issue_id} の処理に失敗しました: {e}"
                )
                self.redis_client.release_lock(lock_key)
                raise

        logger.info("No assignable issues with a defined branch name found.")
        return None
