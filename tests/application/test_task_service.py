import pytest
from unittest.mock import MagicMock, call

from github_broker.application.task_service import TaskService
from github_broker.interface.models import TaskResponse

@pytest.fixture
def task_service_components():
    """Set up mock clients and TaskService instance for tests."""
    mock_github_client = MagicMock()
    mock_redis_client = MagicMock()
    mock_gemini_client = MagicMock()
    repo_name = "test/repo"
    task_service = TaskService(
        github_client=mock_github_client,
        redis_client=mock_redis_client,
        gemini_client=mock_gemini_client,
        repo_name=repo_name
    )
    return task_service, mock_github_client, mock_redis_client, mock_gemini_client, repo_name

def test_request_task_success_first_task(task_service_components):
    """
    Test the successful assignment of a task to an agent with no previous task.
    """
    task_service, mock_github_client, mock_redis_client, mock_gemini_client, repo_name = task_service_components
    agent_id = "test-agent-001"
    capabilities = ["python", "fastapi"]

    mock_redis_client.acquire_lock.return_value = True
    mock_redis_client.get_assignment.return_value = None

    mock_issue = MagicMock()
    mock_issue.id = 12345
    mock_issue.number = 123
    mock_issue.title = "Fix the bug"
    mock_issue.body = "There is a bug that needs fixing."
    mock_label = MagicMock()
    mock_label.name = "bug"
    mock_issue.labels = [mock_label]
    mock_issue.html_url = "https://github.com/test/repo/issues/123"
    mock_github_client.get_open_issues.return_value = [mock_issue]

    mock_gemini_client.select_best_issue_id.return_value = mock_issue.number

    result = task_service.request_task(agent_id, capabilities)

    mock_redis_client.acquire_lock.assert_called_once()
    mock_redis_client.get_assignment.assert_called_once_with(agent_id)
    mock_github_client.remove_label.assert_not_called()

    mock_github_client.add_label.assert_called_once_with(
        repo_name=repo_name,
        issue_id=mock_issue.number,
        label=f"in-progress:{agent_id}"
    )
    
    expected_issues_for_gemini = [{
        "id": mock_issue.number,
        "title": mock_issue.title,
        "body": mock_issue.body,
        "labels": [label.name for label in mock_issue.labels]
    }]
    mock_gemini_client.select_best_issue_id.assert_called_once_with(
        expected_issues_for_gemini, capabilities
    )

    expected_branch_name = f"feature/issue-{mock_issue.number}"
    mock_github_client.create_branch.assert_called_once_with(
        repo_name=repo_name,
        branch_name=expected_branch_name
    )

    mock_redis_client.set_assignment.assert_called_once_with(agent_id, mock_issue.number)

    assert isinstance(result, TaskResponse)
    assert result.issue_id == mock_issue.number
    assert result.title == mock_issue.title
    assert result.branch_name == expected_branch_name
    mock_redis_client.release_lock.assert_called_once()

def test_request_task_no_issues_available(task_service_components):
    task_service, mock_github_client, mock_redis_client, mock_gemini_client, _ = task_service_components
    agent_id = "test-agent-002"
    capabilities = ["react", "frontend"]
    mock_redis_client.acquire_lock.return_value = True
    mock_redis_client.get_assignment.return_value = None
    mock_github_client.get_open_issues.return_value = []

    result = task_service.request_task(agent_id, capabilities)

    assert result is None
    mock_gemini_client.select_best_issue_id.assert_not_called()
    mock_github_client.create_branch.assert_not_called()
    mock_redis_client.release_lock.assert_called_once()

def test_request_task_with_previous_task(task_service_components):
    task_service, mock_github_client, mock_redis_client, mock_gemini_client, repo_name = task_service_components
    agent_id = "test-agent-003"
    capabilities = ["python"]
    previous_issue_number = 999

    mock_redis_client.acquire_lock.return_value = True
    mock_redis_client.get_assignment.return_value = previous_issue_number

    new_mock_issue = MagicMock()
    new_mock_issue.id = 12456
    new_mock_issue.number = 124
    new_mock_issue.title = "A new task"
    new_mock_issue.body = "Details for the new task."
    new_mock_issue.labels = []
    new_mock_issue.html_url = "https://github.com/test/repo/issues/124"
    mock_github_client.get_open_issues.return_value = [new_mock_issue]

    mock_gemini_client.select_best_issue_id.return_value = new_mock_issue.number

    result = task_service.request_task(agent_id, capabilities)

    mock_github_client.remove_label.assert_called_once_with(
        repo_name=repo_name,
        issue_id=previous_issue_number,
        label=f"in-progress:{agent_id}"
    )
    mock_github_client.add_label.assert_has_calls([
        call(repo_name=repo_name, issue_id=previous_issue_number, label="needs-review"),
        call(repo_name=repo_name, issue_id=new_mock_issue.number, label=f"in-progress:{agent_id}")
    ])

    assert result is not None
    assert result.issue_id == new_mock_issue.number