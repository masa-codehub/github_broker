import pytest
from unittest.mock import MagicMock, call

from github_broker.application.task_service import TaskService
from github_broker.interface.models import TaskResponse

VALID_ISSUE_BODY = """
Some description here.

## ブランチ名
feature/valid-issue

## 成果物
- `src/main.py`
"""

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
    task_service, mock_github_client, mock_redis_client, mock_gemini_client, repo_name = task_service_components
    agent_id = "test-agent-001"
    capabilities = ["python", "fastapi"]

    mock_redis_client.acquire_lock.return_value = True
    mock_redis_client.get_assignment.return_value = None

    mock_issue = MagicMock()
    mock_issue.id = 12345
    mock_issue.number = 123
    mock_issue.title = "Fix the bug"
    mock_issue.body = VALID_ISSUE_BODY # Use valid body
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

    # The branch name should be parsed from the issue body
    expected_branch_name = "feature/valid-issue"
    mock_github_client.create_branch.assert_called_once_with(
        repo_name=repo_name,
        branch_name=expected_branch_name
    )

    mock_redis_client.set_assignment.assert_called_once_with(agent_id, mock_issue.number)

    assert isinstance(result, TaskResponse)
    assert result.issue_id == mock_issue.number
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
    new_mock_issue.body = VALID_ISSUE_BODY
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

def test_select_best_issue_filters_issues_without_definitions(task_service_components):
    """Test that issues without proper definitions are filtered out."""
    task_service, mock_github_client, mock_redis_client, mock_gemini_client, _ = task_service_components

    mock_valid_issue = MagicMock()
    mock_valid_issue.number = 1
    mock_valid_issue.title = "Valid Issue"
    mock_valid_issue.body = VALID_ISSUE_BODY
    mock_valid_issue.labels = []

    mock_missing_branch = MagicMock()
    mock_missing_branch.number = 2
    mock_missing_branch.title = "Missing Branch"
    mock_missing_branch.body = "## 成果物\n- `file.txt`"
    mock_missing_branch.labels = []

    mock_empty_deliverables = MagicMock()
    mock_empty_deliverables.number = 3
    mock_empty_deliverables.title = "Empty Deliverables"
    mock_empty_deliverables.body = "## ブランチ名\nfeature/empty\n\n## 成果物\n"
    mock_empty_deliverables.labels = []
    
    mock_no_body = MagicMock()
    mock_no_body.number = 4
    mock_no_body.title = "No Body Issue"
    mock_no_body.body = None
    mock_no_body.labels = []

    mock_github_client.get_open_issues.return_value = [
        mock_valid_issue, 
        mock_missing_branch, 
        mock_empty_deliverables,
        mock_no_body
    ]
    mock_gemini_client.select_best_issue_id.return_value = None

    task_service._select_best_issue(capabilities=["python"])

    expected_issues_for_gemini = [{
        "id": mock_valid_issue.number,
        "title": mock_valid_issue.title,
        "body": mock_valid_issue.body,
        "labels": []
    }]
    mock_gemini_client.select_best_issue_id.assert_called_once_with(
        expected_issues_for_gemini, ["python"]
    )