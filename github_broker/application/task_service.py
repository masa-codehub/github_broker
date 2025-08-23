import logging
import os
import re

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

    def _extract_branch_name_from_issue(
        self,
        issue_body: str,
        issue_id: int,
    ) -> str | None:
        """Issue本文からブランチ名を抽出します。見つからない場合はNoneを返します。"""
        if issue_body:
            match = re.search(r"## ブランチ名\s*\n\s*`?([^`\n]+)`?", issue_body)
            if match:
                branch_name = match.group(1).strip()
                branch_name = branch_name.replace("issue-xx", f"issue-{issue_id}")
                logger.info(f"Issue本文からブランチ名を抽出しました: {branch_name}")
                return branch_name

        logger.warning(
            f"Issue #{issue_id} の本文にブランチ名が見つかりませんでした。このIssueはスキップされます。"
        )
        return None

    def request_task(self, agent_id: str) -> TaskResponse | None:
        """
        GitHubからアサイン可能なIssueを探し、ロックして、タスク情報を返します。
        アサイン可能なIssueとは、オープンであり、かつ本文にブランチ名が指定されているものです。
        """
        logger.info(f"Searching for open issues in repository: {self.repo_name}")
        open_issues = self.github_client.get_open_issues(self.repo_name)

        if not open_issues:
            logger.info("No open issues found.")
            return None

        for issue in open_issues:
            branch_name = self._extract_branch_name_from_issue(
                issue.body,
                issue.number,
            )

            if not branch_name:
                continue

            lock_key = f"issue_lock_{issue.id}"
            logger.info(f"Attempting to acquire lock for issue #{issue.number}")
            if not self.redis_client.acquire_lock(lock_key, "locked", timeout=600):
                logger.warning(
                    f"Issue #{issue.number} のロック取得に失敗しました。他のエージェントによってロックされている可能性があります。スキップします。"
                )
                continue

            try:
                logger.info(f"Lock acquired for issue #{issue.number}. Assigning task.")
                self.github_client.add_label(
                    self.repo_name, issue.number, "in-progress"
                )
                self.github_client.add_label(self.repo_name, issue.number, agent_id)
                logger.info(f"Assigned agent '{agent_id}' to issue #{issue.number}.")

                self.github_client.create_branch(self.repo_name, branch_name)

                return TaskResponse(
                    issue_id=issue.number,
                    issue_url=issue.html_url,
                    title=issue.title,
                    body=issue.body or "",
                    labels=[label.name for label in issue.labels],
                    branch_name=branch_name,
                )
            except Exception as e:
                logger.error(
                    f"ロック取得後にIssue #{issue.number} の処理に失敗しました: {e}"
                )
                self.redis_client.release_lock(lock_key)
                raise

        logger.info("No assignable issues with a defined branch name found.")
        return None
