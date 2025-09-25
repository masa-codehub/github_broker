import logging
from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor


@pytest.fixture
def mock_redis_client():
    """Redisクライアントのモックを提供します。"""
    return MagicMock()


@pytest.fixture
def mock_github_client():
    """GitHubクライアントのモックを提供します。"""
    return MagicMock()


@pytest.fixture
def task_service(mock_redis_client, mock_github_client):
    """TaskServiceのテストインスタンスを提供します。"""
    mock_settings = MagicMock()
    mock_settings.GITHUB_REPOSITORY = "test/repo"
    mock_settings.GITHUB_INDEXING_WAIT_SECONDS = 0

    mock_gemini_executor_instance = MagicMock(spec=GeminiExecutor)
    mock_gemini_executor_instance.build_prompt.return_value = (
        "Generated Prompt for Issue 2"
    )

    return TaskService(
        redis_client=mock_redis_client,
        github_client=mock_github_client,
        settings=mock_settings,
        gemini_executor=mock_gemini_executor_instance,
    )


def create_mock_issue(
    number,
    title,
    body,
    labels,
    html_url_base="https://github.com/test/repo/issues",
    has_branch_name: bool = True,
):
    """テスト用のIssue辞書を生成するヘルパー関数。"""
    full_body = body
    if has_branch_name:
        full_body += f"""

## ブランチ名
`feature/issue-{number}`"""

    return {
        "number": number,
        "title": title,
        "body": full_body,
        "html_url": f"{html_url_base}/{number}",
        "labels": [{"name": label} for label in labels],
    }


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_find_first_assignable_task_exception_releases_lock(
    mock_sleep, task_service, mock_github_client, mock_redis_client
):
    """
    _find_first_assignable_task内で例外が発生した場合にロックが解放されることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""
## 成果物
- test.py""",
        labels=["BACKENDCODER"],
    )
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.add_label.side_effect = Exception("GitHub API Error")

    candidate_issues = [issue]
    agent_id = "test-agent"

    # Act & Assert
    with pytest.raises(Exception, match="GitHub API Error"):
        task_service._find_first_assignable_task(candidate_issues, agent_id)

    mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_find_first_assignable_task_create_branch_exception_releases_lock(
    mock_sleep, task_service, mock_github_client, mock_redis_client
):
    """
    _find_first_assignable_task内でcreate_branchが例外を発生させた場合にロックが解放されることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""
## 成果物
- test.py""",
        labels=["BACKENDCODER"],
    )
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.create_branch.side_effect = Exception("Branch Creation Error")

    candidate_issues = [issue]
    agent_id = "test-agent"

    # Act & Assert
    with pytest.raises(Exception, match="Branch Creation Error"):
        task_service._find_first_assignable_task(candidate_issues, agent_id)

    mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_find_first_assignable_task_rollback_labels_on_branch_creation_failure(
    mock_sleep, task_service, mock_github_client, mock_redis_client, caplog
):
    """
    _find_first_assignable_task内でcreate_branchが例外を発生させた場合に、
    付与されたラベルがロールバックされることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""
## 成果物
- test.py""",
        labels=["BACKENDCODER"],
    )
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.create_branch.side_effect = GithubException(
        status=422, data="Branch already exists"
    )

    candidate_issues = [issue]
    agent_id = "test-agent"

    with caplog.at_level(logging.ERROR):
        # Act & Assert
        with pytest.raises(GithubException, match="Branch already exists"):
            task_service._find_first_assignable_task(candidate_issues, agent_id)

        # Assert
        # ロックが解放されたことを確認
        mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")
        # 付与されたラベルが削除されたことを確認
        mock_github_client.update_issue.assert_called_once_with(
            issue_id=issue["number"], remove_labels=["in-progress", agent_id]
        )


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_find_first_assignable_task_rollback_failure_logs_error(
    mock_sleep, task_service, mock_github_client, mock_redis_client, caplog
):
    """
    _find_first_assignable_task内でcreate_branchが例外を発生させ、
    さらにラベルのロールバックも失敗した場合に、エラーがログに記録されることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""
## 成果物
- test.py""",
        labels=["BACKENDCODER"],
    )
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.create_branch.side_effect = GithubException(
        status=422, data="Branch already exists"
    )
    mock_github_client.update_issue.side_effect = Exception("Rollback Error")

    candidate_issues = [issue]
    agent_id = "test-agent"

    with caplog.at_level(logging.ERROR):
        # Act & Assert
        with pytest.raises(GithubException, match="Branch already exists"):
            task_service._find_first_assignable_task(candidate_issues, agent_id)

        # Assert
        # ロックが解放されたことを確認
        mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")
        # ロールバック処理自体でエラーが発生した場合もログに記録されることを確認
        assert "Failed to rollback labels: Rollback Error" in caplog.text
        # update_issueが呼び出されたことを確認
        mock_github_client.update_issue.assert_called_once()


@pytest.mark.unit
def test_find_first_assignable_task_skips_non_assignable(
    task_service, mock_redis_client
):
    """is_assignable()がFalseを返すIssueをスキップすることをテストします。"""
    # Arrange
    issue_not_assignable = create_mock_issue(
        number=1,
        title="Not Assignable",
        body="No deliverables section",
        labels=["BACKENDCODER"],
        has_branch_name=True,
    )
    issue_assignable = create_mock_issue(
        number=2, title="Assignable", body="## 成果物\n- work", labels=["BACKENDCODER"]
    )
    candidate_issues = [issue_not_assignable, issue_assignable]
    mock_redis_client.acquire_lock.return_value = True

    # Act
    result = task_service._find_first_assignable_task(candidate_issues, "test-agent")

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_2", "locked", timeout=600
    )


@pytest.mark.unit
def test_find_first_assignable_task_skips_no_branch_name(
    task_service, mock_redis_client
):
    """ブランチ名が本文にないIssueをスキップすることをテストします。"""
    # Arrange
    issue_no_branch = create_mock_issue(
        number=1,
        title="No Branch",
        body="## 成果物\n- work",
        labels=["BACKENDCODER"],
        has_branch_name=False,
    )
    issue_with_branch = create_mock_issue(
        number=2,
        title="With Branch",
        body="## 成果物\n- work",
        labels=["BACKENDCODER"],
        has_branch_name=True,
    )
    candidate_issues = [issue_no_branch, issue_with_branch]
    mock_redis_client.acquire_lock.return_value = True

    # Act
    result = task_service._find_first_assignable_task(candidate_issues, "test-agent")

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_2", "locked", timeout=600
    )


@pytest.mark.unit
def test_find_first_assignable_task_skips_locked_issue(task_service, mock_redis_client):
    """RedisでロックされているIssueをスキップすることをテストします。"""
    # Arrange
    issue_locked = create_mock_issue(
        number=1,
        title="Locked Issue",
        body="## 成果物\n- work",
        labels=["BACKENDCODER"],
    )
    issue_unlocked = create_mock_issue(
        number=2,
        title="Unlocked Issue",
        body="## 成果物\n- work",
        labels=["BACKENDCODER"],
    )
    candidate_issues = [issue_locked, issue_unlocked]
    mock_redis_client.acquire_lock.side_effect = [False, True]

    # Act
    result = task_service._find_first_assignable_task(candidate_issues, "test-agent")

    # Assert
    assert result is not None
    assert result.issue_id == 2
    assert mock_redis_client.acquire_lock.call_count == 2
    mock_redis_client.acquire_lock.assert_any_call(
        "issue_lock_1", "locked", timeout=600
    )
    mock_redis_client.acquire_lock.assert_any_call(
        "issue_lock_2", "locked", timeout=600
    )
