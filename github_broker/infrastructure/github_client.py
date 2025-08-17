import logging
import os

from github import Github, GithubException


class GitHubClient:
    """
    GitHub APIと対話するためのクライアント。
    """

    def __init__(self):
        token = os.getenv("GH_TOKEN")
        if not token:
            raise ValueError("GH_TOKEN環境変数にGitHubトークンが見つかりません。")
        self._client = Github(token)

    def get_open_issues(self, repo_name: str):
        """
        進行中でなく、レビューを必要としないすべてのオープンなIssueを取得します。
        クエリはシンプルで、状態ラベルの有無に依存しています。
        """
        try:
            query = f'repo:{repo_name} is:issue is:open -label:"in-progress" -label:"needs-review"'
            logging.info(f"クエリ: {query} でアサイン可能なIssueを検索中")
            issues = self._client.search_issues(query=query)
            logging.info(
                f"アサイン可能なIssueが {issues.totalCount} 件見つかりました。"
            )
            return list(issues)
        except GithubException as e:
            logging.error(
                f"リポジトリ {repo_name} のIssue検索中にエラーが発生しました: {e}"
            )
            raise

    def find_issues_by_labels(self, repo_name: str, labels: list[str]):
        """
        指定されたすべてのラベルを持つIssue（オープンまたはクローズ済み）を検索します。
        この実装は、検索インデックスの遅延を避けるために、すべてのIssueを取得し手動でフィルタリングします。
        """
        try:
            repo = self._client.get_repo(repo_name)
            # Get all issues (open and closed)
            all_issues = repo.get_issues(state="all")

            required_labels = set(labels)

            for issue in all_issues:
                # Get the set of labels for the current issue
                issue_labels = {label.name for label in issue.labels}

                # Check if all required labels are present in the issue's labels
                if required_labels.issubset(issue_labels):
                    logging.info(
                        f"ラベル {issue_labels} を持つ一致するIssue #{issue.number} が見つかりました。"
                    )
                    return issue

            logging.info(f"必要なラベルを持つIssueは見つかりませんでした: {labels}")
            return None

        except GithubException as e:
            logging.error(
                f"リポジトリ {repo_name} でラベルによるIssue検索中にエラーが発生しました: {e}"
            )
            raise

    def add_label(self, repo_name: str, issue_id: int, label: str):
        """
        特定のIssueにラベルを追加します。
        """
        try:
            repo = self._client.get_repo(repo_name)
            issue = repo.get_issue(number=issue_id)
            issue.add_to_labels(label)
            return True
        except GithubException as e:
            logging.error(
                f"リポジトリ {repo_name} のIssue #{issue_id} にラベルを追加中にエラーが発生しました: {e}"
            )
            raise

    def remove_label(self, repo_name: str, issue_id: int, label: str):
        """
        特定のIssueからラベルを削除します。
        Issueにラベルが存在しない場合、警告をログに記録しますが、エラーは発生させません。
        """
        try:
            repo = self._client.get_repo(repo_name)
            issue = repo.get_issue(number=issue_id)
            issue.remove_from_labels(label)
            logging.info(
                f"Issue #{issue_id} からラベル '{label}' を正常に削除しました。"
            )
            return True
        except GithubException as e:
            if e.status == 404:
                logging.warning(
                    f"削除中にIssue #{issue_id} にラベル '{label}' が見つかりませんでした。これは致命的なエラーではないため、続行します。"
                )
                return True
            logging.error(
                f"リポジトリ {repo_name} のIssue #{issue_id} からラベルを削除中にエラーが発生しました: {e}"
            )
            raise

    def create_branch(
        self, repo_name: str, branch_name: str, base_branch: str = "main"
    ):
        """
        ベースブランチから新しいブランチを作成します。
        """
        try:
            repo = self._client.get_repo(repo_name)
            source = repo.get_branch(base_branch)
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)
            return True
        except GithubException as e:
            if e.status == 422 and "Reference already exists" in str(e.data):
                logging.warning(
                    f"リポジトリ {repo_name} にブランチ '{branch_name}' は既に存在します。続行します。"
                )
                return True
            logging.error(
                f"リポジトリ {repo_name} にブランチ {branch_name} を作成中にエラーが発生しました: {e}"
            )
            raise
