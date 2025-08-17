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
            raise ValueError("GITHUB_REPOSITORY environment variable is not set.")

    def _generate_branch_name(self, issue_id: int, issue_title: str) -> str:
        """Issueタイトルからブランチ名を生成します。"""
        # タイトルを小文字に変換
        title = issue_title.lower()
        # 英数字以外の文字をハイフンに置換
        title = re.sub(r"[^a-z0-9]+", "-", title).strip("-")
        # 複数のハイフンを1つにまとめる
        title = re.sub(r"-+", "-", title)
        # 50文字に切り詰める
        title = title[:50].strip("-")
        return f"feature/issue-{issue_id}-{title}"

    def request_task(self) -> TaskResponse | None:
        """
        GitHubからアサイン可能なIssueを探し、ロックして、タスク情報を返します。
        """
        logger.info(f"Searching for open issues in repository: {self.repo_name}")
        open_issues = self.github_client.get_open_issues(self.repo_name)

        if not open_issues:
            logger.info("No assignable issues found.")
            return None

        # 最初のオープンなIssueを選択
        issue = open_issues[0]
        lock_key = f"issue_lock_{issue.id}"

        logger.info(f"Attempting to acquire lock for issue #{issue.number}")
        if not self.redis_client.acquire_lock(lock_key, "locked", timeout=600):
            logger.warning(
                f"Issue #{issue.number} のロック取得に失敗しました。他のエージェントによってロックされている可能性があります。"
            )
            return None

        try:
            logger.info(f"Lock acquired for issue #{issue.number}. Assigning task.")
            # Issueに"in-progress"ラベルを追加
            self.github_client.add_label(self.repo_name, issue.number, "in-progress")

            # ブランチ名を作成
            branch_name = self._generate_branch_name(issue.number, issue.title)
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
                f"Failed to process issue #{issue.number} after acquiring lock: {e}"
            )
            # エラーが発生した場合はロックを解放
            self.redis_client.release_lock(lock_key)
            raise
