import os
from unittest.mock import MagicMock, patch

import pytest
from github import GithubException
from github.Issue import Issue
from github.Label import Label

from github_broker.application.task_service import TaskService
from github_broker.interface.models import TaskResponse


@pytest.fixture
def mock_redis_client():
    return MagicMock()


@pytest.fixture
def mock_github_client():
    return MagicMock()


@pytest.fixture
def task_service(mock_redis_client, mock_github_client):
    with patch.dict(os.environ, {"GITHUB_REPOSITORY": "test/repo"}):
        return TaskService(
            redis_client=mock_redis_client,
            github_client=mock_github_client,
        )


@pytest.fixture
def issue_with_branch():
    issue = MagicMock(spec=Issue)
    issue.id = 1
    issue.number = 123
    issue.title = "Test Issue With Branch"
    issue.body = "This is a test issue.\n\n## ブランチ名\n`feature/issue-123-test`"
    issue.html_url = "https://github.com/test/repo/issues/123"
    label = MagicMock(spec=Label)
    label.name = "bug"
    issue.labels = [label]
    return issue


@pytest.fixture
def issue_without_branch():
    issue = MagicMock(spec=Issue)
    issue.id = 2
    issue.number = 456
    issue.title = "Test Issue Without Branch"
    issue.body = "This issue has no branch name."
    issue.html_url = "https://github.com/test/repo/issues/456"
    issue.labels = []
    return issue


def test_request_task_no_open_issues(task_service, mock_github_client):
    """Tests that None is returned when there are no open issues."""
    mock_github_client.get_open_issues.return_value = []
    result = task_service.request_task("test-agent")
    assert result is None


def test_request_task_no_assignable_issues(
    task_service, mock_github_client, issue_without_branch
):
    """Tests that None is returned when no issues have a branch name."""
    mock_github_client.get_open_issues.return_value = [issue_without_branch]
    result = task_service.request_task("test-agent")
    assert result is None


def test_request_task_skips_issue_without_branch_name(
    task_service,
    mock_redis_client,
    mock_github_client,
    issue_with_branch,
    issue_without_branch,
):
    """Tests that the service skips an issue without a branch name and finds the next one."""
    mock_github_client.get_open_issues.return_value = [
        issue_without_branch,
        issue_with_branch,
    ]
    mock_redis_client.acquire_lock.return_value = True

    result = task_service.request_task("test-agent")

    assert isinstance(result, TaskResponse)
    assert result.issue_id == 123  # The second issue
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_1", "locked", timeout=600
    )


def test_request_task_skips_locked_issue(
    task_service, mock_redis_client, mock_github_client, issue_with_branch
):
    """Tests that the service skips a locked issue and finds the next one."""
    issue2_with_branch = MagicMock(spec=Issue)
    issue2_with_branch.id = 3
    issue2_with_branch.number = 789
    issue2_with_branch.title = "Second Test Issue"
    issue2_with_branch.body = "## ブランチ名\n`feature/issue-789-another`"
    issue2_with_branch.html_url = "https://github.com/test/repo/issues/789"
    issue2_with_branch.labels = []

    mock_github_client.get_open_issues.return_value = [
        issue_with_branch,
        issue2_with_branch,
    ]
    # Fail lock for the first issue, succeed for the second
    mock_redis_client.acquire_lock.side_effect = [False, True]

    result = task_service.request_task("test-agent")

    assert isinstance(result, TaskResponse)
    assert result.issue_id == 789  # The second issue
    assert mock_redis_client.acquire_lock.call_count == 2
    mock_redis_client.acquire_lock.assert_any_call(
        "issue_lock_1", "locked", timeout=600
    )
    mock_redis_client.acquire_lock.assert_any_call(
        "issue_lock_3", "locked", timeout=600
    )


def test_request_task_success(
    task_service, mock_redis_client, mock_github_client, issue_with_branch
):
    """Tests a successful task assignment."""
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.get_open_issues.return_value = [issue_with_branch]

    result = task_service.request_task("test-agent")

    assert isinstance(result, TaskResponse)
    assert result.issue_id == 123
    assert result.title == "Test Issue With Branch"
    assert result.branch_name == "feature/issue-123-test"
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_1", "locked", timeout=600
    )
    mock_github_client.add_label.assert_any_call("test/repo", 123, "in-progress")
    mock_github_client.add_label.assert_any_call("test/repo", 123, "test-agent")
    mock_github_client.create_branch.assert_called_once_with(
        "test/repo", "feature/issue-123-test"
    )


def test_request_task_exception_after_lock(
    task_service, mock_redis_client, mock_github_client, issue_with_branch
):
    """Tests that the lock is released if an exception occurs after locking."""
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.get_open_issues.return_value = [issue_with_branch]
    mock_github_client.add_label.side_effect = GithubException(
        status=500, data={}, headers=None
    )

    with pytest.raises(GithubException):
        task_service.request_task("test-agent")

    mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")


def test_extract_branch_name_from_issue_found(task_service):
    """Tests that a branch name is correctly extracted from the issue body."""
    body = "Some text\n## ブランチ名\n`feature/issue-42-new-feature`\nMore text"
    branch_name = task_service._extract_branch_name_from_issue(body, 42)
    assert branch_name == "feature/issue-42-new-feature"


def test_extract_branch_name_from_issue_not_found(task_service):
    """Tests that None is returned when no branch name is found in the body."""
    body = "Some text without branch name"
    branch_name = task_service._extract_branch_name_from_issue(body, 42)
    assert branch_name is None


def test_extract_branch_name_with_issue_xx_replacement(task_service):
    """Tests that 'issue-xx' is correctly replaced with the actual issue number."""
    body = "## ブランチ名\n`feature/issue-xx-cool-feature`"
    branch_name = task_service._extract_branch_name_from_issue(body, 99)
    assert branch_name == "feature/issue-99-cool-feature"
