import os
import time
from unittest.mock import MagicMock, patch

import pytest
from github import Github, GithubException

from github_broker.infrastructure.github_client import GitHubClient


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_add_label_success(mock_github, mock_getenv):
    """
    add_labelが正しいパラメータでGitHubライブラリを呼び出すことを確認するテスト。
    """
    # Arrange
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_repo.get_issue.return_value = mock_issue
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    repo_name = "test/repo"
    issue_id = 123
    label_to_add = "in-progress"

    # Act
    result = client.add_label(repo_name, issue_id, label_to_add)

    # Assert
    mock_github_instance.get_repo.assert_called_once_with(repo_name)
    mock_repo.get_issue.assert_called_once_with(number=issue_id)
    mock_issue.add_to_labels.assert_called_once_with(label_to_add)
    assert result is True


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_remove_label_success(mock_github, mock_getenv):
    """
    remove_labelが正しいパラメータでGitHubライブラリを呼び出すことを確認するテスト。
    """
    # Arrange
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_repo.get_issue.return_value = mock_issue
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    repo_name = "test/repo"
    issue_id = 123
    label_to_remove = "in-progress"

    # Act
    result = client.remove_label(repo_name, issue_id, label_to_remove)

    # Assert
    mock_github_instance.get_repo.assert_called_once_with(repo_name)
    mock_repo.get_issue.assert_called_once_with(number=issue_id)
    mock_issue.remove_from_labels.assert_called_once_with(label_to_remove)
    assert result is True


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_create_branch_success(mock_github, mock_getenv):
    """
    create_branchが正しいパラメータでGitHubライブラリを呼び出すことを確認するテスト。
    """
    # Arrange
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_source_branch = MagicMock()
    mock_source_branch.commit.sha = "abcdef123456"
    mock_repo.get_branch.return_value = mock_source_branch
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    repo_name = "test/repo"
    branch_name = "feature/new-thing"
    base_branch = "main"

    # Act
    result = client.create_branch(repo_name, branch_name, base_branch)

    # Assert
    mock_github_instance.get_repo.assert_called_once_with(repo_name)
    mock_repo.get_branch.assert_called_once_with(base_branch)
    mock_repo.create_git_ref.assert_called_once_with(
        ref=f"refs/heads/{branch_name}", sha="abcdef123456"
    )
    assert result is True


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_find_issues_by_labels_found(mock_github, mock_getenv):
    """find_issues_by_labelsがラベルにマッチしたときに正しいIssueを返すことをテストします。"""
    # Arrange
    mock_getenv.return_value = "fake_token"

    # モックラベルを作成
    mock_label_a = MagicMock()
    mock_label_a.name = "label-a"
    mock_label_b = MagicMock()
    mock_label_b.name = "label-b"
    mock_label_c = MagicMock()
    mock_label_c.name = "label-c"

    # モックIssueを作成
    issue1 = MagicMock()
    issue1.number = 1
    issue1.labels = [mock_label_a]

    issue2 = MagicMock()
    issue2.number = 2
    issue2.labels = [mock_label_a, mock_label_b]  # これが探しているもの

    issue3 = MagicMock()
    issue3.number = 3
    issue3.labels = [mock_label_b, mock_label_c]

    mock_repo = MagicMock()
    mock_repo.get_issues.return_value = [issue1, issue2, issue3]

    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()

    # Act
    found_issue = client.find_issues_by_labels("test/repo", ["label-a", "label-b"])

    # Assert
    assert found_issue is not None
    assert found_issue.number == 2
    mock_github_instance.get_repo.assert_called_once_with("test/repo")
    mock_repo.get_issues.assert_called_once_with(state="all")


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_find_issues_by_labels_not_found(mock_github, mock_getenv):
    """find_issues_by_labelsがすべてのラベルにマッチするIssueがない場合にNoneを返すことをテストします。"""
    # Arrange
    mock_getenv.return_value = "fake_token"

    mock_label_a = MagicMock()
    mock_label_a.name = "label-a"
    mock_label_b = MagicMock()
    mock_label_b.name = "label-b"

    issue1 = MagicMock()
    issue1.labels = [mock_label_a]

    mock_repo = MagicMock()
    mock_repo.get_issues.return_value = [issue1]

    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()

    # Act
    found_issue = client.find_issues_by_labels("test/repo", ["label-a", "label-b"])

    # Assert
    assert found_issue is None


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_get_open_issues_raises_exception(mock_github, mock_getenv):
    """get_open_issuesがAPI呼び出し失敗時に例外を送出することをテストします。"""
    mock_getenv.return_value = "fake_token"
    mock_github_instance = MagicMock()
    mock_github_instance.search_issues.side_effect = GithubException(
        status=500, data={}, headers=None
    )
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    with pytest.raises(GithubException):
        client.get_open_issues("test/repo")


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_find_issues_by_labels_raises_exception(mock_github, mock_getenv):
    """find_issues_by_labelsがAPI呼び出し失敗時に例外を送出することをテストします。"""
    mock_getenv.return_value = "fake_token"
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.side_effect = GithubException(
        status=500, data={}, headers=None
    )
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    with pytest.raises(GithubException):
        client.find_issues_by_labels("test/repo", ["label"])


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_add_label_raises_exception(mock_github, mock_getenv):
    """add_labelがAPI呼び出し失敗時に例外を送出することをテストします。"""
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_repo.get_issue.side_effect = GithubException(status=500, data={}, headers=None)
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    with pytest.raises(GithubException):
        client.add_label("test/repo", 123, "label")


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_remove_label_raises_exception(mock_github, mock_getenv):
    """remove_labelが404以外のエラーで例外を送出することをテストします。"""
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_repo.get_issue.side_effect = GithubException(
        status=500, data={}, headers=None
    )  # 500エラー
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    with pytest.raises(GithubException):
        client.remove_label("test/repo", 123, "label")


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_create_branch_raises_exception(mock_github, mock_getenv):
    """create_branchが422以外のエラーで例外を送出することをテストします。"""
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_repo.get_branch.side_effect = GithubException(
        status=500, data={}, headers=None
    )  # 500エラー
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    with pytest.raises(GithubException):
        client.create_branch("test/repo", "branch")


@patch("os.getenv")
def test_init_raises_value_error_if_no_token(mock_getenv):
    """__init__がGITHUB_TOKEN未設定時にValueErrorを送出することをテストします。"""
    mock_getenv.return_value = None
    with pytest.raises(
        ValueError, match="GITHUB_TOKEN環境変数にGitHubトークンが見つかりません。"
    ):
        GitHubClient()


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_remove_label_handles_404(mock_github, mock_getenv):
    """remove_labelが404エラーを正常に処理することをテストします。"""
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_issue.remove_from_labels.side_effect = GithubException(
        status=404, data={}, headers=None
    )
    mock_repo.get_issue.return_value = mock_issue
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    result = client.remove_label("test/repo", 123, "non-existent-label")
    assert result is True  # 例外を送出しないはず


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_create_branch_handles_422(mock_github, mock_getenv):
    """create_branchが422エラー（ブランチ重複）を正常に処理することをテストします。"""
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_repo.create_git_ref.side_effect = GithubException(
        status=422, data={"message": "Reference already exists"}, headers=None
    )
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    result = client.create_branch("test/repo", "existing-branch")
    assert result is True  # 例外を送出しないはず


# --- 統合テスト ---

# 環境変数が設定されていない場合にテストをスキップするためのマーカー
requires_github_token = pytest.mark.skipif(
    not os.getenv("GITHUB_TOKEN") or not os.getenv("GITHUB_REPOSITORY"),
    reason="統合テストにはGITHUB_TOKENおよびGITHUB_REPOSITORY環境変数が必要です",
)


@pytest.fixture(scope="module")
def github_client():
    """統合テスト用のGitHubClientインスタンスを提供します。"""
    return GitHubClient()


@pytest.fixture(scope="module")
def test_repo_name():
    """環境変数からリポジトリ名を提供します。"""
    return os.getenv("GITHUB_REPOSITORY")


@pytest.fixture(scope="module")
def raw_github_client():
    """テストのセットアップとティアダウンのために生のPyGithubインスタンスを提供します。"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN is not set.")
    return Github(token)


@requires_github_token
def test_integration_lifecycle(github_client, test_repo_name, raw_github_client):
    """
    Issueとブランチ管理の完全なライフサイクルをテストします。
    この単一のテストは、アトミック性を確保し、リポジトリ内の孤立したテストデータを防ぐために、
    セットアップ、実行、クリーンアップを組み合わせています。
    """
    repo = raw_github_client.get_repo(test_repo_name)

    # --- テストデータ ---
    unique_id = int(time.time())
    issue_to_filter_title = f"フィルターされるべきテストIssue - {unique_id}"
    issue_to_keep_title = f"保持されるべきテストIssue - {unique_id}"
    label_in_progress = "in-progress"
    label_to_add_remove = f"test-label-{unique_id}"
    branch_to_create = f"feature/test-branch-{unique_id}"

    issue_to_filter = None
    issue_to_keep = None

    try:
        # 1. --- セットアップ ---
        # get_open_issuesをテストするために2つのIssueを作成
        issue_to_filter = repo.create_issue(
            title=issue_to_filter_title, body="このIssueは除外されるべきです。"
        )
        issue_to_filter.add_to_labels(label_in_progress)

        issue_to_keep = repo.create_issue(
            title=issue_to_keep_title, body="このIssueは返されるべきです。"
        )

        # GitHub APIが新しいIssueとラベルを処理するのを少し待つ
        time.sleep(5)

        # 2. --- get_open_issuesのテスト ---
        print("--- 実行中: get_open_issuesのテスト ---")
        open_issues = github_client.get_open_issues(test_repo_name)

        # フィルタリングされなくなったため、両方のIssueが含まれることを確認
        issue_numbers = [issue.number for issue in open_issues]
        print(f"見つかったオープンなIssue番号: {issue_numbers}")
        print(
            f"Issue #{issue_to_keep.number} と Issue #{issue_to_filter.number} の両方が見つかることを期待しています"
        )

        assert issue_to_keep.number in issue_numbers
        assert issue_to_filter.number in issue_numbers
        print("--- PASSED: get_open_issuesのテスト ---")

        # 3. --- add_labelとremove_labelのテスト ---
        print(
            f"--- 実行中: Issue #{issue_to_keep.number} のadd_labelとremove_labelのテスト ---"
        )
        # ラベルを追加
        github_client.add_label(
            test_repo_name, issue_to_keep.number, label_to_add_remove
        )
        time.sleep(2)
        issue_reloaded = repo.get_issue(issue_to_keep.number)
        assert label_to_add_remove in [label.name for label in issue_reloaded.labels]
        print(f"ラベル '{label_to_add_remove}' の追加に成功しました")

        # ラベルを削除
        github_client.remove_label(
            test_repo_name, issue_to_keep.number, label_to_add_remove
        )
        time.sleep(2)
        issue_reloaded = repo.get_issue(issue_to_keep.number)
        assert label_to_add_remove not in [
            label.name for label in issue_reloaded.labels
        ]
        print(f"ラベル '{label_to_add_remove}' の削除に成功しました")
        print("--- PASSED: add_labelとremove_labelのテスト ---")

        # 4. --- create_branchのテスト ---
        print("--- 実行中: create_branchのテスト ---")
        github_client.create_branch(
            test_repo_name, branch_to_create, base_branch="main"
        )
        time.sleep(2)
        # ブランチの存在を確認
        try:
            repo.get_branch(branch_to_create)
            branch_exists = True
        except GithubException as e:
            if e.status == 404:
                branch_exists = False
            else:
                raise
        assert branch_exists, f"ブランチ '{branch_to_create}' が作成されませんでした。"
        print(f"ブランチ '{branch_to_create}' の作成に成功しました")
        print("--- PASSED: create_branchのテスト ---")

    finally:
        # 5. --- クリーンアップ ---
        print("--- 実行中: クリーンアップ ---")
        # Issueをクローズ
        if issue_to_filter:
            print(f"Issue #{issue_to_filter.number} をクローズ中")
            issue_to_filter.edit(state="closed")
        if issue_to_keep:
            print(f"Issue #{issue_to_keep.number} をクローズ中")
            issue_to_keep.edit(state="closed")

        # ブランチを削除
        try:
            ref = repo.get_git_ref(f"heads/{branch_to_create}")
            print(f"ブランチ '{branch_to_create}' を削除中")
            ref.delete()
        except GithubException as e:
            if e.status != 404:  # ブランチが存在しない場合は無視
                print(
                    f"警告: ブランチ '{branch_to_create}' を削除できませんでした: {e}"
                )
        print("--- クリーンアップ完了 ---")
