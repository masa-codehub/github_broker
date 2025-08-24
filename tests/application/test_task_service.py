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
def test_request_task_selects_best_match(
    mock_sleep, task_service, mock_github_client, mock_redis_client
):
    """Capabilityと最も多く一致し、割り当て可能なIssueが選択されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1,
        title="Docs update",
        body="## 成果物\n- README.md",
        labels=["documentation"],
    )
    issue2 = create_mock_issue(
        number=2, title="Bug fix", body="## 成果物\n- fix.py", labels=["bug", "python"]
    )
    issue3 = create_mock_issue(
        number=3,
        title="Feature dev",
        body="## 成果物\n- feature.py",
        labels=["feature", "python", "fastapi"],
    )
    issue4_no_deliverable = create_mock_issue(
        number=4,
        title="Refactor",
        body="no deliverables section",
        labels=["refactor", "python", "fastapi", "bug"],
    )

    mock_github_client.get_open_issues.return_value = [
        issue1,
        issue2,
        issue3,
        issue4_no_deliverable,
    ]
    mock_github_client.search_issues.return_value = []  # complete_previous_taskが何もしないようにする
    mock_redis_client.acquire_lock.return_value = True

    agent_capabilities = ["python", "fastapi", "feature", "testing"]

    # Act
    result = task_service.request_task(
        agent_id="test-agent", capabilities=agent_capabilities
    )

    # Assert
    # issue3が3つ一致で最も優先度が高い
    assert result is not None
    assert result.issue_id == 3
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_3", "locked", timeout=600
    )


@patch("time.sleep", return_value=None)
def test_request_task_no_matching_issue(mock_sleep, task_service, mock_github_client):
    """エージェントのCapabilityに一致するIssueがない場合にNoneが返されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1, title="Docs", body="", labels=["documentation"]
    )
    mock_github_client.get_open_issues.return_value = [issue1]
    agent_capabilities = ["python", "bugfix"]

    # Act
    result = task_service.request_task(
        agent_id="test-agent", capabilities=agent_capabilities
    )

    # Assert
    assert result is None


@patch("time.sleep", return_value=None)
def test_request_task_no_assignable_issue(mock_sleep, task_service, mock_github_client):
    """一致するIssueはあるが、どれも割り当て可能でない（成果物セクションがない）場合にNoneが返されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1, title="Feature", body="body without deliverables", labels=["python"]
    )
    mock_github_client.get_open_issues.return_value = [issue1]
    agent_capabilities = ["python"]

    # Act
    result = task_service.request_task(
        agent_id="test-agent", capabilities=agent_capabilities
    )

    # Assert
    assert result is None


@patch("time.sleep", return_value=None)
def test_request_task_skips_locked_issue(
    mock_sleep, task_service, mock_github_client, mock_redis_client
):
    """最も優先度の高いIssueがロックされている場合、次に優先度の高いIssueが選択されることをテストします。"""
    # Arrange
    issue_high_priority = create_mock_issue(
        number=1,
        title="High prio",
        body="## 成果物\n- fix.py",
        labels=["python", "bug"],
    )
    issue_low_priority = create_mock_issue(
        number=2, title="Low prio", body="## 成果物\n- doc.md", labels=["documentation"]
    )
    mock_github_client.get_open_issues.return_value = [
        issue_high_priority,
        issue_low_priority,
    ]
    mock_github_client.search_issues.return_value = []  # complete_previous_taskが何もしないようにする
    mock_redis_client.acquire_lock.side_effect = [
        False,
        True,
    ]  # 1番目は失敗、2番目は成功

    agent_capabilities = ["python", "bug", "documentation"]

    # Act
    result = task_service.request_task(
        agent_id="test-agent", capabilities=agent_capabilities
    )

    # Assert
    assert result is not None
    assert result.issue_id == 2  # 2番目のIssueが選択される
    assert mock_redis_client.acquire_lock.call_count == 2


@patch("time.sleep", return_value=None)
def test_request_task_skips_issue_without_branch_name(
    mock_sleep, task_service, mock_github_client, mock_redis_client
):
    """「成果物」はあるがブランチ名がないIssueをスキップすることをテストします。"""
    # Arrange
    issue_no_branch = create_mock_issue(
        number=1,
        title="No branch name",
        body="## 成果物\n- some deliverable",
        labels=["python"],
        has_branch_name=False,
    )
    issue_with_branch = create_mock_issue(
        number=2,
        title="With branch name",
        body="## 成果物\n- another deliverable",
        labels=["python"],
    )
    mock_github_client.get_open_issues.return_value = [
        issue_no_branch,
        issue_with_branch,
    ]
    mock_github_client.search_issues.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    agent_capabilities = ["python"]

    # Act
    result = task_service.request_task(
        agent_id="test-agent", capabilities=agent_capabilities
    )

    # Assert
    assert result is not None
    assert result.issue_id == 2  # 2番目のIssueが選択される
