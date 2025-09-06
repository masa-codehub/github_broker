import os
from unittest.mock import MagicMock, patch

import pytest
from github.Issue import Issue
from github.Label import Label

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


def create_mock_issue(number, title, body, labels, has_branch_name: bool = True):
    """テスト用のIssueモックを生成するヘルパー関数。"""
    issue = MagicMock(spec=Issue)
    issue.number = number
    issue.title = title

    full_body = body
    if has_branch_name:
        full_body += f"\n\n## ブランチ名\n`feature/issue-{number}`"

    issue.body = full_body
    issue.html_url = f"https://github.com/test/repo/issues/{number}"

    mock_labels = []
    for label_name in labels:
        mock_label = MagicMock(spec=Label)
        mock_label.name = label_name
        mock_labels.append(mock_label)
    issue.labels = mock_labels
    return issue


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
    mock_github_client.search_issues.return_value = []
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
    mock_github_client.get_open_issues.assert_called_once()


@patch("time.time")
@patch("time.sleep", return_value=None)
def test_request_task_times_out(
    mock_sleep, mock_time, task_service, mock_github_client
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
        number=1, title="Delayed Task", body="## 成果物\n- delayed.py", labels=["BACKENDCODER"]
    )
    # 最初の呼び出しではタスクなし、2回目で見つかる
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
    mock_sleep.assert_any_call(5) # ポーリング間隔でsleepが呼ばれる


@patch("time.sleep", return_value=None)
def test_request_task_no_matching_issue_no_wait(
    mock_sleep, task_service, mock_github_client
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
