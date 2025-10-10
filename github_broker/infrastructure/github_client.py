import logging

from github import Github, GithubException
from github.PullRequest import PullRequest


class GitHubClient:
    """
    GitHub APIと対話するためのクライアント。
    """

    def __init__(self, github_repository: str, github_token: str):
        self._repo_name = github_repository
        self._client = Github(github_token)

    def get_open_issues(self):
        """
        リポジトリに存在するすべてのオープンなIssueを取得します。
        """
        try:
            query = f'repo:{self._repo_name} is:issue is:open -label:"needs-review"'
            logging.info(f"クエリ: {query} でオープンなIssueを検索中")
            issues = self._client.search_issues(query=query)
            logging.info(f"オープンなIssueが {issues.totalCount} 件見つかりました。")
            return [issue.raw_data for issue in issues]
        except GithubException as e:
            logging.error(
                f"リポジトリ {self._repo_name} のIssue検索中にエラーが発生しました: {e}"
            )
            raise

    def find_issues_by_labels(self, labels: list[str]):
        """
        指定されたすべてのラベルを持つIssue（オープンまたはクローズ済み）を検索します。
        """
        try:
            labels_query = " ".join([f'label:"{label}"' for label in labels])
            query = f"repo:{self._repo_name} is:issue {labels_query}"
            logging.info(f"クエリ: {query} でIssueを検索中")
            issues = self._client.search_issues(query=query)
            logging.info(f"{issues.totalCount} 件のIssueが見つかりました。")
            return [issue.raw_data for issue in issues]
        except GithubException as e:
            logging.error(
                f"An error occurred while searching for issues by labels in repo {self._repo_name}: {e}"
            )
            raise

    def add_label(self, issue_id: int, label: str):
        """
        特定のIssueにラベルを追加します。
        """
        try:
            repo = self._client.get_repo(self._repo_name)
            issue = repo.get_issue(number=issue_id)
            issue.add_to_labels(label)
            return True
        except GithubException as e:
            logging.error(
                f"リポジトリ {self._repo_name} のIssue #{issue_id} にラベルを追加中にエラーが発生しました: {e}"
            )
            raise

    def update_issue(
        self,
        issue_id: int,
        remove_labels: list[str] | None = None,
        add_labels: list[str] | None = None,
    ):
        """
        特定のIssueのラベルを更新します。
        """
        try:
            repo = self._client.get_repo(self._repo_name)
            issue = repo.get_issue(number=issue_id)

            if remove_labels:
                for label_name in remove_labels:
                    try:
                        issue.remove_from_labels(label_name)
                        logging.info(
                            f"Issue #{issue_id} からラベル '{label_name}' を削除しました。"
                        )
                    except GithubException as e:
                        if e.status == 404:
                            logging.warning(
                                f"削除中にIssue #{issue_id} にラベル '{label_name}' が見つかりませんでした。スキップします。"
                            )
                        else:
                            raise

            if add_labels:
                for label_name in add_labels:
                    issue.add_to_labels(label_name)
                    logging.info(
                        f"Issue #{issue_id} にラベル '{label_name}' を追加しました。"
                    )
            return True
        except GithubException as e:
            logging.error(
                f"リポジトリ {self._repo_name} のIssue #{issue_id} のラベル更新中にエラーが発生しました: {e}"
            )
            raise

    def remove_label(self, issue_id: int, label: str):
        """
        特定のIssueからラベルを削除します。
        Issueにラベルが存在しない場合、警告をログに記録しますが、エラーは発生させません。
        """
        try:
            repo = self._client.get_repo(self._repo_name)
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
                f"リポジトリ {self._repo_name} のIssue #{issue_id} からラベルを削除中にエラーが発生しました: {e}"
            )
            raise

    def create_branch(self, branch_name: str, base_branch: str = "main"):
        """
        ベースブランチから新しいブランチを作成します。
        """
        try:
            repo = self._client.get_repo(self._repo_name)
            source = repo.get_branch(base_branch)
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)
            return True
        except GithubException as e:
            if e.status == 422 and "Reference already exists" in str(e.data):
                logging.warning(
                    f"リポジトリ {self._repo_name} にブランチ '{branch_name}' は既に存在します。続行します。"
                )
                return True
            logging.error(
                f"リポジトリ {self._repo_name} にブランチ {branch_name} を作成中にエラーが発生しました: {e}"
            )
            raise

    def get_pull_request_info_from_issue(self, issue_number: int) -> dict | None:
        """
        Issue番号から、そのIssueに紐づくPull Requestの情報を取得します。
        PRが存在しない場合はNoneを返します。
        """
        try:
            # Issue番号が本文に含まれるオープンなPRを検索
            query = f"repo:{self._repo_name} is:pr is:open in:body {issue_number}"
            logging.info(f"クエリ: {query} でPRを検索中")
            pull_requests = self._client.search_issues(query=query)

            if pull_requests.totalCount > 0:
                # 最初のPRを返す（通常、Issueに紐づくPRは1つと想定）
                pr = pull_requests[0]
                logging.info(
                    f"Issue #{issue_number} に紐づくPR #{pr.number} が見つかりました。"
                )
                return pr.raw_data
            logging.info(f"Issue #{issue_number} に紐づくPRは見つかりませんでした。")
            return None
        except GithubException as e:
            logging.error(
                f"リポジトリ {self._repo_name} のIssue #{issue_number} に紐づくPRの検索中にエラーが発生しました: {e}"
            )
            raise

    def get_pr_for_issue(self, issue_number: int) -> PullRequest | None:
        """
        Issue番号に紐づくPull Requestオブジェクトを取得します。
        """
        try:
            query = f"repo:{self._repo_name} is:pr is:open in:body #{issue_number}"
            prs = self._client.search_issues(query=query)
            if prs.totalCount == 0:
                return None

            pr_issue = prs[0]
            repo = self._client.get_repo(self._repo_name)
            return repo.get_pull(pr_issue.number)
        except GithubException as e:
            logging.error(
                f"Error getting PR for issue {issue_number} in repo {self._repo_name}: {e}"
            )
            raise

    def add_label_to_pr(self, pr_number: int, label: str) -> None:
        """
        特定のPull Requestにラベルを追加します。
        """
        try:
            repo = self._client.get_repo(self._repo_name)
            pr = repo.get_pull(pr_number)
            issue = repo.get_issue(pr.number)
            issue.add_to_labels(label)
            logging.info(f"Added label '{label}' to PR #{pr_number}")
        except GithubException as e:
            logging.error(
                f"Error adding label to PR #{pr_number} in repo {self._repo_name}: {e}"
            )
            raise

    def get_issue_by_number(self, issue_number: int):
        """
        特定のIssue番号に対応するIssueの生データを取得します。
        """
        try:
            repo = self._client.get_repo(self._repo_name)
            issue = repo.get_issue(number=issue_number)
            return issue.raw_data
        except GithubException as e:
            logging.error(
                f"リポジトリ {self._repo_name} からIssue #{issue_number} の取得中にエラーが発生しました: {e}"
            )
            raise

    def get_pull_request_review_comments(self, pull_number: int) -> list[dict]:
        """
        特定のPull Requestに関するすべてのレビューコメントを取得します。

        Args:
            pull_number: レビューコメントを取得するPull Requestの番号。

        Returns:
            Pull Requestに関連付けられたレビューコメントのリスト。
            各コメントは辞書形式で表現されます。

        Raises:
            GithubException: API呼び出し中にエラーが発生した場合。
        """
        try:
            repo = self._client.get_repo(self._repo_name)
            pull = repo.get_pull(number=pull_number)
            comments = pull.get_review_comments()
            logging.info(
                f"Pull Request #{pull_number} から {len(list(comments))} 件のレビューコメントを取得しました。"
            )
            return [comment.raw_data for comment in comments]
        except GithubException as e:
            logging.error(
                f"リポジトリ {self._repo_name} のPull Request #{pull_number} のレビューコメント取得中にエラーが発生しました: {e}"
            )
            raise
