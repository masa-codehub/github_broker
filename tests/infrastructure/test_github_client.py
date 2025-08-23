import os
import time
from unittest.mock import MagicMock, patch

import pytest
from github import Github, GithubException

from github_broker.infrastructure.github_client import GitHubClient


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_get_open_issues_filters_in_progress(mock_github, mock_getenv):
    """
    get_open_issuesが'in-progress'ラベルを持つIssueを除外することを確認するテスト。
    """
    # Arrange
    mock_getenv.return_value = "fake_token"

    mock_issue_in_progress = MagicMock()
    mock_issue_in_progress.number = 1
    mock_issue_in_progress.title = "In Progress Issue"
    mock_label_in_progress = MagicMock()
    mock_label_in_progress.name = "in-progress"
    mock_issue_in_progress.labels = [mock_label_in_progress]

    mock_issue_open = MagicMock()
    mock_issue_open.number = 2
    mock_issue_open.title = "Open Issue"
    mock_issue_open.labels = []

    # フィルタリングされた場合に返されるPaginatedListオブジェクトをモック
    mock_search_result_filtered = MagicMock()
    mock_search_result_filtered.totalCount = 1
    mock_search_result_filtered.__iter__.return_value = [mock_issue_open]

    # このモックはsearch_issuesメソッドの動作をシミュレートします
    def search_issues_side_effect(query):
        # クエリが'in-progress'でフィルタリングされている場合、フィルタリングされたリストを返す
        if '-label:"in-progress"' in query:
            return mock_search_result_filtered
        # それ以外の場合は、フィルタリングされていないリストを返すか、エラーを発生させることができます
        # このテストでは、フィルタリングされた呼び出しのみを期待します
        return MagicMock()

    mock_github_instance = MagicMock()
    mock_github_instance.search_issues.side_effect = search_issues_side_effect
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    repo_name = "test/repo"

    # Act
    issues = client.get_open_issues(repo_name)

    # Assert
    expected_query = (
        f'repo:{repo_name} is:issue is:open -label:"in-progress" -label:"needs-review"'
    )
    mock_github_instance.search_issues.assert_called_once_with(query=expected_query)

    assert len(issues) == 1
    assert issues[0].title == "Open Issue"


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
    """
    Test that find_issues_by_labels returns the correct issue when labels match.
    """
    # Arrange
    mock_getenv.return_value = "fake_token"

    # Create mock labels
    mock_label_a = MagicMock()
    mock_label_a.name = "label-a"
    mock_label_b = MagicMock()
    mock_label_b.name = "label-b"
    mock_label_c = MagicMock()
    mock_label_c.name = "label-c"

    # Create mock issues
    issue1 = MagicMock()
    issue1.number = 1
    issue1.labels = [mock_label_a]

    issue2 = MagicMock()
    issue2.number = 2
    issue2.labels = [mock_label_a, mock_label_b]  # This is the one we want

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
    """
    Test that find_issues_by_labels returns None when no issue matches all labels.
    """
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
    """Test that get_open_issues raises an exception when the API call fails."""
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
    """Test that find_issues_by_labels raises an exception when the API call fails."""
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
    """Test that add_label raises an exception when the API call fails."""
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
    """Test that remove_label raises an exception for non-404 errors."""
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_repo.get_issue.side_effect = GithubException(
        status=500, data={}, headers=None
    )  # 500 error
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    with pytest.raises(GithubException):
        client.remove_label("test/repo", 123, "label")


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_create_branch_raises_exception(mock_github, mock_getenv):
    """Test that create_branch raises an exception for non-422 errors."""
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_repo.get_branch.side_effect = GithubException(
        status=500, data={}, headers=None
    )  # 500 error
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    with pytest.raises(GithubException):
        client.create_branch("test/repo", "branch")


@patch("os.getenv")
def test_init_raises_value_error_if_no_token(mock_getenv):
    """Test that __init__ raises ValueError if GITHUB_TOKEN is not set."""
    mock_getenv.return_value = None
    with pytest.raises(
        ValueError, match="GITHUB_TOKEN環境変数にGitHubトークンが見つかりません。"
    ):
        GitHubClient()


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_remove_label_handles_404(mock_github, mock_getenv):
    """Test that remove_label handles 404 errors gracefully."""
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
    assert result is True  # Should not re-raise


@patch("os.getenv")
@patch("github_broker.infrastructure.github_client.Github")
def test_create_branch_handles_422(mock_github, mock_getenv):
    """Test that create_branch handles 422 errors gracefully."""
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
    assert result is True  # Should not re-raise


# --- Integration Tests ---

# Marker to skip tests if environment variables are not set
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
    """環境変数からリポジリ名を提供します。"""
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

    # --- Test Data ---
    unique_id = int(time.time())
    issue_to_filter_title = f"Test Issue to be Filtered - {unique_id}"
    issue_to_keep_title = f"Test Issue to be Kept - {unique_id}"
    label_in_progress = "in-progress"
    label_to_add_remove = f"test-label-{unique_id}"
    branch_to_create = f"feature/test-branch-{unique_id}"

    issue_to_filter = None
    issue_to_keep = None

    try:
        # 1. --- SETUP ---
        # Create two issues for testing get_open_issues
        issue_to_filter = repo.create_issue(
            title=issue_to_filter_title, body="This issue should be filtered out."
        )
        issue_to_filter.add_to_labels(label_in_progress)

        issue_to_keep = repo.create_issue(
            title=issue_to_keep_title, body="This issue should be returned."
        )

        # Give GitHub's API a moment to process the new issues and labels
        time.sleep(5)

        # 2. --- TEST get_open_issues ---
        print("--- 実行中: TEST get_open_issues ---")
        open_issues = github_client.get_open_issues(test_repo_name)

        # Assert that the filtered issue is not present and the kept issue is
        issue_numbers = [issue.number for issue in open_issues]
        print(f"見つかったオープンなIssue番号: {issue_numbers}")
        print(
            f"Issue #{issue_to_keep.number} が見つかり、Issue #{issue_to_filter.number} が見つからないことを期待しています"
        )

        assert issue_to_keep.number in issue_numbers
        assert issue_to_filter.number not in issue_numbers
        print("--- PASSED: TEST get_open_issues ---")

        # 3. --- TEST add_label and remove_label ---
        print(
            f"--- Running: TEST add_label and remove_label for issue #{issue_to_keep.number} ---"
        )
        # Add a label
        github_client.add_label(
            test_repo_name, issue_to_keep.number, label_to_add_remove
        )
        time.sleep(2)
        issue_reloaded = repo.get_issue(issue_to_keep.number)
        assert label_to_add_remove in [label.name for label in issue_reloaded.labels]
        print(f"Successfully added label '{label_to_add_remove}'")

        # Remove the label
        github_client.remove_label(
            test_repo_name, issue_to_keep.number, label_to_add_remove
        )
        time.sleep(2)
        issue_reloaded = repo.get_issue(issue_to_keep.number)
        assert label_to_add_remove not in [
            label.name for label in issue_reloaded.labels
        ]
        print(f"Successfully removed label '{label_to_add_remove}'")
        print("--- PASSED: TEST add_label and remove_label ---")

        # 4. --- TEST create_branch ---
        print("--- Running: TEST create_branch ---")
        github_client.create_branch(
            test_repo_name, branch_to_create, base_branch="main"
        )
        time.sleep(2)
        # Verify branch exists
        try:
            repo.get_branch(branch_to_create)
            branch_exists = True
        except GithubException as e:
            if e.status == 404:
                branch_exists = False
            else:
                raise
        assert branch_exists, f"Branch '{branch_to_create}' was not created."
        print(f"Successfully created branch '{branch_to_create}'")
        print("--- PASSED: TEST create_branch ---")

    finally:
        # 5. --- CLEANUP ---
        print("--- Running: Cleanup ---")
        # Close issues
        if issue_to_filter:
            print(f"Closing issue #{issue_to_filter.number}")
            issue_to_filter.edit(state="closed")
        if issue_to_keep:
            print(f"Closing issue #{issue_to_keep.number}")
            issue_to_keep.edit(state="closed")

        # Delete branch
        try:
            ref = repo.get_git_ref(f"heads/{branch_to_create}")
            print(f"Deleting branch '{branch_to_create}'")
            ref.delete()
        except GithubException as e:
            if e.status != 404:  # Ignore if branch doesn't exist
                print(f"Warning: Could not delete branch '{branch_to_create}': {e}")
        print("--- Cleanup Finished ---")


# このファイルが直接実行された場合にテストを実行するためのエントリーポイント
if __name__ == "__main__":
    pytest.main()
