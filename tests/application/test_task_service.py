import os
from unittest.mock import MagicMock, patch

import pytest

from github_broker.application.task_service import TaskService


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
    with patch.dict(os.environ, {"GITHUB_REPOSITORY": "test/repo"}):
        return TaskService(
            redis_client=mock_redis_client,
            github_client=mock_github_client,
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
        full_body += f"\n\n## ブランチ名\n`feature/issue-{number}`"

    return {
        "number": number,
        "title": title,
        "body": full_body,
        "html_url": f"{html_url_base}/{number}",
        "labels": [{"name": label} for label in labels],
    }


@patch("time.sleep", return_value=None)
def test_request_task_selects_by_role_no_wait(
    mock_sleep, task_service, mock_github_client, mock_redis_client
):
    """エージェントの役割（role）に一致するラベルを持つIssueが即時選択されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1,
        title="Irrelevant Task",
        body="## 成果物\n- README.md",
        labels=["documentation"],
    )
    issue2 = create_mock_issue(
        number=2,
        title="Backend Task",
        body="## 成果物\n- feature.py",
        labels=["feature", "BACKENDCODER"],
    )

    mock_github_client.get_open_issues.return_value = [issue1, issue2]
    mock_redis_client.acquire_lock.return_value = True

    agent_role = "BACKENDCODER"

    # Act
    result = task_service.request_task(
        agent_id="test-agent", agent_role=agent_role, timeout=0
    )

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_2", "locked", timeout=600
    )
    assert mock_github_client.get_open_issues.call_count == 1


@patch("time.time")
@patch("time.sleep", return_value=None)
def test_request_task_times_out(
    mock_sleep, mock_time, task_service, mock_github_client, mock_redis_client
):
    """利用可能なタスクがなく、タイムアウトする場合をテストします。"""
    # Arrange
    mock_github_client.get_open_issues.return_value = []
    timeout = 10
    # time.time()が最初にtimeoutを返し、その後増加してタイムアウトするように設定
    mock_time.side_effect = [0, 2, 4, 6, 8, 11]

    # Act
    result = task_service.request_task(
        agent_id="test-agent", agent_role="BACKENDCODER", timeout=timeout
    )

    # Assert
    assert result is None
    # 5秒間隔でsleepが呼ばれる
    assert mock_sleep.call_count > 1
    assert mock_github_client.get_open_issues.call_count > 1


@patch("time.time")
@patch("time.sleep", return_value=None)
def test_request_task_finds_task_after_polling(
    mock_sleep, mock_time, task_service, mock_github_client, mock_redis_client
):
    """ポーリング後にタスクが見つかる場合をテストします。"""
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Delayed Task",
        body="## 成果物\n- delayed.py",
        labels=["BACKENDCODER"],
    )
    # 最初の呼び出しではタスクなし、2回目以降は見つかるように設定
    mock_github_client.get_open_issues.side_effect = [[], [issue]]
    mock_redis_client.acquire_lock.return_value = True
    timeout = 10
    mock_time.side_effect = [0, 5, 11]  # 1回ポーリングして見つかる

    # Act
    result = task_service.request_task(
        agent_id="test-agent", agent_role="BACKENDCODER", timeout=timeout
    )

    # Assert
    assert result is not None
    assert result.issue_id == 1
    assert mock_github_client.get_open_issues.call_count == 2
    mock_sleep.assert_called()  # ポーリング間隔でsleepが呼ばれる


@patch("time.sleep", return_value=None)
def test_request_task_no_matching_issue_no_wait(
    mock_sleep, task_service, mock_github_client, mock_redis_client
):
    """エージェントの役割に一致するIssueがない場合にNoneが返されることをテストします（待機なし）。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1, title="Docs", body="", labels=["documentation"]
    )
    mock_github_client.get_open_issues.return_value = [issue1]
    agent_role = "BACKENDCODER"

    # Act
    result = task_service.request_task(
        agent_id="test-agent", agent_role=agent_role, timeout=0
    )

    # Assert
    assert result is None


@patch("time.sleep", return_value=None)
def test_request_task_excludes_needs_review_label(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """'needs-review'ラベルを持つIssueがタスク割り当てから除外されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1,
        title="Task Needs Review",
        body="## 成果物\n- review.py",
        labels=["BACKENDCODER", "needs-review"],
    )
    issue2 = create_mock_issue(
        number=2,
        title="Assignable Task",
        body="## 成果物\n- assign.py",
        labels=["BACKENDCODER"],
    )
    mock_github_client.get_open_issues.return_value = [issue1, issue2]
    mock_redis_client.acquire_lock.return_value = True

    # Act
    result = task_service.request_task(
        agent_id="test-agent", agent_role="BACKENDCODER", timeout=0
    )

    # Assert
    assert result is not None
    assert result.issue_id == 2  # issue1は除外され、issue2が選択されるはず


@patch("time.sleep", return_value=None)
def test_complete_previous_task_updates_issues(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """
    complete_previous_taskが、in-progressとagent_idラベルを持つIssueを更新することをテストします。
    """
    # Arrange
    mock_issue = create_mock_issue(
        number=101,
        title="Test Issue",
        body="",
        labels=["in-progress", "test-agent"],
    )
    # GitHubからin-progressとagent_idラベルを持つIssueを取得することを想定
    mock_github_client.find_issues_by_labels.return_value = [mock_issue]

    agent_id = "test-agent"

    # Act
    task_service.complete_previous_task(agent_id)

    # Assert
    mock_github_client.find_issues_by_labels.assert_called_once_with(
        repo_name="test/repo", labels=["in-progress", agent_id]
    )
    mock_github_client.update_issue.assert_called_once_with(
        repo_name="test/repo",
        issue_id=mock_issue["number"],
        remove_labels=["in-progress", agent_id],
        add_labels=["needs-review"],
    )


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
        body="## 成果物\n- test.py",
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
        body="## 成果物\n- test.py",
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


def test_task_service_init_no_github_repository_env():
    """
    GITHUB_REPOSITORY環境変数が設定されていない場合にValueErrorが発生することをテストします。
    """
    # Arrange
    original_env = os.environ.copy()
    if "GITHUB_REPOSITORY" in os.environ:
        del os.environ["GITHUB_REPOSITORY"]

    # Act & Assert
    with pytest.raises(
        ValueError, match="GITHUB_REPOSITORY環境変数が設定されていません。"
    ):
        TaskService(redis_client=MagicMock(), github_client=MagicMock())

    # Cleanup
    os.environ.clear()
    os.environ.update(original_env)
