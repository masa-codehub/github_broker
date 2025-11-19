import logging
import os
import time
from unittest.mock import MagicMock, patch

import pytest
from github import Github, GithubException

from github_broker.infrastructure.github_client import GitHubClient


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_add_label_success(mock_github):
    """
    add_labelが正しいパラメータでGitHubライブラリを呼び出すことを確認するテスト。
    """
    # Arrange
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_repo.get_issue.return_value = mock_issue
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    issue_id = 123
    label_to_add = "in-progress"

    # Act
    result = client.add_label(issue_id, label_to_add)

    # Assert
    mock_repo.get_issue.assert_called_once_with(number=issue_id)
    mock_issue.add_to_labels.assert_called_once_with(label_to_add)
    assert result is True


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_remove_label_success(mock_github):
    """
    remove_labelが正しいパラメータでGitHubライブラリを呼び出すことを確認するテスト。
    """
    # Arrange
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_repo.get_issue.return_value = mock_issue
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    issue_id = 123
    label_to_remove = "in-progress"

    # Act
    result = client.remove_label(issue_id, label_to_remove)

    # Assert
    mock_repo.get_issue.assert_called_once_with(number=issue_id)
    mock_issue.remove_from_labels.assert_called_once_with(label_to_remove)
    assert result is True


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_create_branch_success(mock_github):
    """
    create_branchが正しいパラメータでGitHubライブラリを呼び出すことを確認するテスト。
    """
    # Arrange
    mock_repo = MagicMock()
    mock_source_branch = MagicMock()
    mock_source_branch.commit.sha = "abcdef123456"
    mock_repo.get_branch.return_value = mock_source_branch
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    branch_name = "feature/new-thing"
    base_branch = "main"

    # Act
    result = client.create_branch(branch_name, base_branch)

    # Assert
    mock_repo.get_branch.assert_called_once_with(base_branch)
    mock_repo.create_git_ref.assert_called_once_with(
        ref=f"refs/heads/{branch_name}", sha="abcdef123456"
    )
    assert result is True


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_find_issues_by_labels_found(mock_github):
    """find_issues_by_labelsがラベルにマッチしたときに正しいIssueを返すことをテストします。"""
    # Arrange
    # モックIssueを作成
    issue2 = MagicMock()
    issue2.raw_data = {"number": 2}

    mock_search_results = MagicMock()
    mock_search_results.totalCount = 1
    mock_search_results.__iter__.return_value = [issue2]

    mock_github_instance = MagicMock()
    mock_github_instance.search_issues.return_value = mock_search_results
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")

    # Act
    found_issues = client.find_issues_by_labels(["label-a", "label-b"])

    # Assert
    assert found_issues is not None
    assert len(found_issues) == 1
    assert found_issues[0]["number"] == 2
    mock_github_instance.search_issues.assert_called_once_with(
        query='repo:test/repo is:issue label:"label-a" label:"label-b"'
    )


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_find_issues_by_labels_not_found(mock_github):
    """find_issues_by_labelsがすべてのラベルにマッチするIssueがない場合に空のリストを返すことをテストします。"""
    # Arrange
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

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")

    # Act
    found_issues = client.find_issues_by_labels(["label-a", "label-b"])

    # Assert
    assert found_issues == []


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_get_open_issues_raises_exception(mock_github):
    """get_open_issuesがAPI呼び出し失敗時に例外を送出することをテストします。"""
    mock_github_instance = MagicMock()
    mock_github_instance.search_issues.side_effect = GithubException(
        status=500, data={}, headers=None
    )
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    with pytest.raises(GithubException):
        client.get_open_issues()


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_get_open_issues_success(mock_github):
    """get_open_issuesが正常にIssueを返すことをテストします。"""
    # Arrange
    mock_issue = MagicMock()
    mock_issue.raw_data = {"number": 1, "title": "Test Issue"}
    mock_results = MagicMock()
    mock_results.totalCount = 1
    mock_results.__iter__.return_value = [mock_issue]
    mock_github_instance = MagicMock()
    mock_github_instance.search_issues.return_value = mock_results
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")

    # Act
    issues = client.get_open_issues()

    # Assert
    assert issues == [mock_issue.raw_data]
    mock_github_instance.search_issues.assert_called_once_with(
        query='repo:test/repo is:issue is:open -label:"needs-review"'
    )


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_find_issues_by_labels_raises_exception(mock_github):
    """find_issues_by_labelsがAPI呼び出し失敗時に例外を送出することをテストします。"""
    mock_github_instance = MagicMock()
    mock_github_instance.search_issues.side_effect = GithubException(
        status=500, data={}, headers=None
    )
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    with pytest.raises(GithubException):
        client.find_issues_by_labels(["label"])


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_add_label_raises_exception(mock_github):
    """add_labelがAPI呼び出し失敗時に例外を送出することをテストします。"""
    mock_repo = MagicMock()
    mock_repo.get_issue.side_effect = GithubException(status=500, data={}, headers=None)
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    with pytest.raises(GithubException):
        client.add_label(123, "label")


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_remove_label_raises_exception(mock_github):
    """remove_labelが404以外のエラーで例外を送出することをテストします。"""
    mock_repo = MagicMock()
    mock_repo.get_issue.side_effect = GithubException(
        status=500, data={}, headers=None
    )  # 500エラー
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    with pytest.raises(GithubException):
        client.remove_label(123, "label")


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_create_branch_raises_exception(mock_github):
    """create_branchが422以外のエラーで例外を送出することをテストします。"""
    mock_repo = MagicMock()
    mock_repo.get_branch.side_effect = GithubException(
        status=500, data={}, headers=None
    )  # 500エラー
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    with pytest.raises(GithubException):
        client.create_branch("branch")


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_remove_label_handles_404(mock_github):
    """remove_labelが404エラーを正常に処理することをテストします。"""
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_issue.remove_from_labels.side_effect = GithubException(
        status=404, data={}, headers=None
    )
    mock_repo.get_issue.return_value = mock_issue
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    result = client.remove_label(123, "non-existent-label")
    assert result is True  # 例外を送出しないはず


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_create_branch_handles_422(mock_github):
    """create_branchが422エラー（ブランチ重複）を正常に処理することをテストします。"""
    mock_repo = MagicMock()
    mock_repo.create_git_ref.side_effect = GithubException(
        status=422, data={"message": "Reference already exists"}, headers=None
    )
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    result = client.create_branch("existing-branch")
    assert result is True  # 例外を送出しないはず


@pytest.fixture(scope="module")
def github_client(test_repo_name):
    """統合テスト用のGitHubClientインスタンスを提供します。"""
    return GitHubClient(test_repo_name, os.getenv("GITHUB_TOKEN"))


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


# --- 統合テスト ---
def _wait_for_condition(check_function, expected_value, timeout=30, poll_interval=2):
    """特定の条件が満たされるまでポーリングします。"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_value = check_function()
        if current_value == expected_value:
            return True
        time.sleep(poll_interval)
    raise TimeoutError(
        f"Condition not met within {timeout} seconds. "
        f"Last value: {current_value}, Expected value: {expected_value}"
    )


# 環境変数が設定されていない場合にテストをスキップするためのマーカー
requires_github_token = pytest.mark.skipif(
    not os.getenv("GITHUB_TOKEN") or not os.getenv("GITHUB_REPOSITORY"),
    reason="統合テストにはGITHUB_TOKENおよびGITHUB_REPOSITORY環境変数が必要です",
)


@pytest.fixture(scope="function")
def managed_test_issue(raw_github_client, test_repo_name):
    """
    テスト用のIssueを作成し、テスト終了後に自動的にクローズするフィクスチャ。
    scope="function" により、このフィクスチャを使用する各テスト関数ごとに新しいIssueが作成されます。
    """
    repo = raw_github_client.get_repo(test_repo_name)
    unique_id = int(time.time())
    issue_title = f"統合テスト用Issue - {unique_id}"
    issue = repo.create_issue(
        title=issue_title, body="このIssueはテスト後に自動的にクローズされます。"
    )
    logging.info(
        f"--- SETUP: Issue #{issue.number} ('{issue_title}') を作成しました ---"
    )

    yield issue

    # --- Teardown ---
    logging.info(f"--- TEARDOWN: Issue #{issue.number} をクローズします ---")
    try:
        issue.edit(state="closed")
    except GithubException as e:
        logging.warning(f"警告: Issue #{issue.number} のクローズに失敗しました: {e}")


@pytest.mark.integration
@requires_github_token
def test_integration_add_and_remove_label(
    github_client, test_repo_name, raw_github_client, managed_test_issue
):
    """ラベルの追加と削除のライフサイクルをテストします。"""
    repo = raw_github_client.get_repo(test_repo_name)
    issue = managed_test_issue
    label_name = f"test-label-{int(time.time())}"

    # 1. ラベルを追加
    logging.info(
        f"--- RUN: Issue #{issue.number} にラベル '{label_name}' を追加します ---"
    )
    github_client.add_label(issue.number, label_name)

    # 2. ラベルが追加されたことをポーリングして確認
    def check_labels():
        reloaded_issue = repo.get_issue(issue.number)
        return label_name in [label.name for label in reloaded_issue.labels]

    _wait_for_condition(check_labels, True)
    logging.info(f"--- PASS: ラベル '{label_name}' の追加を確認しました ---")

    # 3. ラベルを削除
    logging.info(
        f"--- RUN: Issue #{issue.number} からラベル '{label_name}' を削除します ---"
    )
    github_client.remove_label(issue.number, label_name)

    # 4. ラベルが削除されたことをポーリングして確認
    _wait_for_condition(check_labels, False)
    logging.info(f"--- PASS: ラベル '{label_name}' の削除を確認しました ---")


@pytest.mark.integration
@requires_github_token
def test_integration_create_and_delete_branch(
    github_client, test_repo_name, raw_github_client
):
    """ブランチの作成と削除のライフサイクルをテストします。"""
    repo = raw_github_client.get_repo(test_repo_name)
    branch_name = f"feature/test-branch-{int(time.time())}"

    try:
        # 1. ブランチを作成
        logging.info(f"--- RUN: ブランチ '{branch_name}' を作成します ---")
        github_client.create_branch(branch_name, base_branch="main")

        # 2. ブランチが作成されたことをポーリングして確認
        def check_branch_exists():
            try:
                repo.get_branch(branch_name)
                return True
            except GithubException as e:
                if e.status == 404:
                    return False
                raise

        _wait_for_condition(check_branch_exists, True)
        logging.info(f"--- PASS: ブランチ '{branch_name}' の作成を確認しました ---")

    finally:
        # 3. ブランチを削除 (Teardown)
        logging.info(f"--- TEARDOWN: ブランチ '{branch_name}' を削除します ---")
        try:
            ref = repo.get_git_ref(f"heads/{branch_name}")
            ref.delete()
        except GithubException as e:
            if e.status != 404:
                logging.warning(
                    f"警告: ブランチ '{branch_name}' の削除に失敗しました: {e}"
                )


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_update_issue_add_and_remove_labels(mock_github):
    """update_issueがラベルの追加と削除を正しく行うことをテストします。"""
    # Arrange
    mock_issue = MagicMock()
    mock_repo = MagicMock()
    mock_repo.get_issue.return_value = mock_issue
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    issue_id = 123
    remove_labels = ["old-label"]
    add_labels = ["new-label"]

    # Act
    result = client.update_issue(issue_id, remove_labels, add_labels)

    # Assert
    assert result is True
    mock_repo.get_issue.assert_called_once_with(number=issue_id)
    mock_issue.remove_from_labels.assert_called_once_with("old-label")
    mock_issue.add_to_labels.assert_called_once_with("new-label")


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_update_issue_remove_nonexistent_label_handles_404(mock_github):
    """update_issueが404エラーをハンドルし、警告をログに出力することをテストします。"""
    # Arrange
    mock_issue = MagicMock()
    mock_issue.remove_from_labels.side_effect = GithubException(
        status=404, data={}, headers=None
    )
    mock_repo = MagicMock()
    mock_repo.get_issue.return_value = mock_issue
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    issue_id = 123
    remove_labels = ["nonexistent-label"]

    # Act
    with patch(
        "github_broker.infrastructure.github_client.logger.warning"
    ) as mock_log_warning:
        result = client.update_issue(issue_id, remove_labels=remove_labels)

    # Assert
    assert result is True
    mock_log_warning.assert_called_once()


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_update_issue_remove_label_raises_exception(mock_github):
    """update_issueがラベル削除時に404以外のエラーで例外を送出することをテストします。"""
    # Arrange
    mock_issue = MagicMock()
    mock_issue.remove_from_labels.side_effect = GithubException(
        status=500, data={}, headers=None
    )
    mock_repo = MagicMock()
    mock_repo.get_issue.return_value = mock_issue
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    issue_id = 123
    remove_labels = ["any-label"]

    # Act & Assert
    with pytest.raises(GithubException):
        client.update_issue(issue_id, remove_labels=remove_labels)


@pytest.mark.unit
@pytest.mark.anyio
@patch("github_broker.infrastructure.github_client.Github")
async def test_get_pull_request_review_comments_success(mock_github):
    """get_pull_request_review_commentsが正常にレビューコメントを返すことをテストします。"""
    # Arrange
    mock_review_comment = MagicMock()
    mock_review_comment.raw_data = {"id": 1, "body": "Test comment"}
    mock_pull = MagicMock()
    mock_pull.get_review_comments.return_value = [mock_review_comment]
    mock_repo = MagicMock()
    mock_repo.get_pull.return_value = mock_pull
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    pull_number = 123

    # Act
    comments = await client.get_pull_request_review_comments(pull_number)

    # Assert
    assert comments == [mock_review_comment.raw_data]
    mock_repo.get_pull.assert_called_once_with(number=pull_number)
    mock_pull.get_review_comments.assert_called_once_with()


@pytest.mark.unit
@pytest.mark.anyio
@patch("github_broker.infrastructure.github_client.Github")
async def test_get_pull_request_review_comments_raises_exception(mock_github):
    """get_pull_request_review_commentsがAPI呼び出し失敗時に例外を送出することをテストします。"""
    # Arrange
    mock_pull = MagicMock()
    mock_pull.get_review_comments.side_effect = GithubException(
        status=500, data={}, headers=None
    )
    mock_repo = MagicMock()
    mock_repo.get_pull.return_value = mock_pull
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    pull_number = 123

    # Act & Assert
    with pytest.raises(GithubException):
        await client.get_pull_request_review_comments(pull_number)








@pytest.mark.unit
@pytest.mark.anyio
@patch("github_broker.infrastructure.github_client.Github")
async def test_get_pull_request_review_comments_uses_cache(mock_github):
    """
    get_pull_request_review_commentsがキャッシュを利用することをテストします。

    - 最初の呼び出しではキャッシュミスとなり、GitHub APIが呼び出され、結果がキャッシュに保存されます。
    - 2回目の呼び出しではキャッシュヒットとなり、GitHub APIは呼び出されません。
    """
    # Arrange
    # RedisClientのモック設定
    mock_redis_client = MagicMock()
    mock_redis_client.get_value.side_effect = [
        None,
        '[{"id": 2, "body": "Cached PR comment"}]',
    ]  # 1回目はミス、2回目はヒット

    # GitHubClientのモック設定
    mock_review_comment = MagicMock()
    mock_review_comment.raw_data = {"id": 1, "body": "Test comment"}
    mock_pull = MagicMock()
    mock_pull.get_review_comments.return_value = [mock_review_comment]
    mock_repo = MagicMock()
    mock_repo.get_pull.return_value = mock_pull
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    pull_number = 123
    client = GitHubClient(
        repo_name, "fake_token", redis_client=mock_redis_client
    )

    # Act - 1回目の呼び出し (キャッシュミスをシミュレート)
    comments_first_call = await client.get_pull_request_review_comments(pull_number)

    # Assert - 1回目の呼び出し
    # Redisから取得を試み、GitHub APIを呼び出し、Redisに保存
    mock_redis_client.get_value.assert_called_once()
    mock_repo.get_pull.assert_called_once_with(number=pull_number)
    mock_pull.get_review_comments.assert_called_once()
    mock_redis_client.set_value.assert_called_once()
    assert comments_first_call == [mock_review_comment.raw_data]

    # Act - 2回目の呼び出し (キャッシュヒットをシミュレート)
    comments_second_call = await client.get_pull_request_review_comments(pull_number)

    # Assert - 2回目の呼び出し
    # Redisから取得を試み、キャッシュヒットのためGitHub APIは呼び出されない
    assert mock_redis_client.get_value.call_count == 2
    mock_repo.get_pull.assert_called_once()  # GitHub APIは2回目は呼び出されない
    mock_pull.get_review_comments.assert_called_once()  # GitHub APIは2回目は呼び出されない
    assert comments_second_call == [{"id": 2, "body": "Cached PR comment"}]

@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_get_pull_request_info_from_issue_found(mock_github):
    """get_pull_request_info_from_issueがPRにマッチしたときに正しいPR情報を返すことをテストします。"""
    # Arrange
    mock_pr = MagicMock()
    mock_pr.raw_data = {
        "number": 1,
        "html_url": "https://github.com/test/repo/pull/1",
        "state": "open",
    }

    mock_search_results = MagicMock()
    mock_search_results.totalCount = 1
    mock_search_results.__getitem__.return_value = mock_pr

    mock_github_instance = MagicMock()
    mock_github_instance.search_issues.return_value = mock_search_results
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    issue_number = 123

    # Act
    pr_info = client.get_pull_request_info_from_issue(issue_number)

    # Assert
    assert pr_info is not None
    assert pr_info["number"] == 1
    assert pr_info["html_url"] == "https://github.com/test/repo/pull/1"
    assert pr_info["state"] == "open"
    mock_github_instance.search_issues.assert_called_once_with(
        query=f"repo:{repo_name} is:pr is:open in:body {issue_number}"
    )


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_get_pull_request_info_from_issue_not_found(mock_github):
    """get_pull_request_info_from_issueがPRにマッチしない場合にNoneを返すことをテストします。"""
    # Arrange
    mock_search_results = MagicMock()
    mock_search_results.totalCount = 0

    mock_github_instance = MagicMock()
    mock_github_instance.search_issues.return_value = mock_search_results
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    issue_number = 123

    # Act
    pr_info = client.get_pull_request_info_from_issue(issue_number)

    # Assert
    assert pr_info is None
    mock_github_instance.search_issues.assert_called_once_with(
        query=f"repo:{repo_name} is:pr is:open in:body {issue_number}"
    )


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_get_pull_request_info_from_issue_raises_exception(mock_github):
    """get_pull_request_info_from_issueがAPI呼び出し失敗時に例外を送出することをテストします。"""
    # Arrange
    mock_github_instance = MagicMock()
    mock_github_instance.search_issues.side_effect = GithubException(
        status=500, data={}, headers=None
    )
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    issue_number = 123

    # Act & Assert
    with pytest.raises(GithubException):
        client.get_pull_request_info_from_issue(issue_number)


@pytest.mark.unit
@patch("github_broker.infrastructure.github_client.Github")
def test_has_pr_label_logs_error_in_japanese(mock_github, caplog):
    """has_pr_labelが例外発生時に日本語でエラーログを出力することをテストします。"""
    # Arrange
    mock_repo = MagicMock()
    mock_repo.get_pull.side_effect = GithubException(status=500, data={}, headers=None)
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    repo_name = "test/repo"
    client = GitHubClient(repo_name, "fake_token")
    pr_number = 123
    label = "test-label"

    # Act & Assert
    with caplog.at_level(logging.ERROR), pytest.raises(GithubException):
        client.has_pr_label(pr_number, label)

    # Assert
    assert (
        "リポジトリ test/repo のPR #123 のラベル 'test-label' を確認中にエラーが発生しました"
        in caplog.text
    )
