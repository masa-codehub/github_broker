import pytest
from unittest.mock import MagicMock, call
from github import UnknownObjectException

from github_broker.application.task_service import TaskService
from github_broker.interface.models import TaskResponse

VALID_ISSUE_BODY = """
Some description here.

## ブランチ名
feature/valid-issue

## 成果物
- `src/main.py`
"""

ISSUE_BODY_NO_BRANCH = """
Some description here.

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
    mock_github_client.find_issues_by_labels.return_value = None

    mock_issue = MagicMock()
    mock_issue.id = 12345
    mock_issue.number = 123
    mock_issue.title = "Fix the bug"
    mock_issue.body = VALID_ISSUE_BODY
    mock_label = MagicMock()
    mock_label.name = "bug"
    mock_issue.labels = [mock_label]
    mock_issue.html_url = "https://github.com/test/repo/issues/123"
    mock_github_client.get_open_issues.return_value = [mock_issue]

    mock_gemini_client.select_best_issue_id.return_value = mock_issue.number

    result = task_service.request_task(agent_id, capabilities)

    mock_redis_client.acquire_lock.assert_called_once()
    mock_github_client.find_issues_by_labels.assert_called_once_with(
        repo_name=repo_name, labels=["in-progress", agent_id]
    )
    mock_github_client.remove_label.assert_not_called()

    mock_github_client.add_label.assert_has_calls([
        call(repo_name=repo_name, issue_id=mock_issue.number, label="in-progress"),
        call(repo_name=repo_name, issue_id=mock_issue.number, label=agent_id)
    ], any_order=True)
    
    expected_issues_for_gemini = [{
        "id": mock_issue.number,
        "title": mock_issue.title,
        "body": mock_issue.body,
        "labels": [label.name for label in mock_issue.labels]
    }]
    mock_gemini_client.select_best_issue_id.assert_called_once_with(
        expected_issues_for_gemini, capabilities
    )

    expected_branch_name = "feature/valid-issue"
    mock_github_client.create_branch.assert_called_once_with(
        repo_name=repo_name,
        branch_name=expected_branch_name
    )

    assert isinstance(result, TaskResponse)
    assert result.issue_id == mock_issue.number
    assert result.branch_name == expected_branch_name
    mock_redis_client.release_lock.assert_called_once()

def test_request_task_no_branch_name(task_service_components):
    """Test that a default branch name is created when not specified in the issue."""
    task_service, mock_github_client, mock_redis_client, mock_gemini_client, repo_name = task_service_components
    agent_id = "test-agent-no-branch"
    capabilities = ["python"]
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.find_issues_by_labels.return_value = None

    mock_issue = MagicMock()
    mock_issue.number = 456
    mock_issue.title = "Task without branch name"
    mock_issue.body = ISSUE_BODY_NO_BRANCH
    mock_issue.labels = []
    mock_issue.html_url = f"https://github.com/test/repo/issues/{mock_issue.number}"
    mock_github_client.get_open_issues.return_value = [mock_issue]
    mock_gemini_client.select_best_issue_id.return_value = mock_issue.number

    result = task_service.request_task(agent_id, capabilities)

    expected_branch_name = f"feature/issue-{mock_issue.number}"
    mock_github_client.create_branch.assert_called_once_with(
        repo_name=repo_name,
        branch_name=expected_branch_name
    )
    assert result.branch_name == expected_branch_name

def test_request_task_no_issues_available(task_service_components):
    task_service, mock_github_client, mock_redis_client, mock_gemini_client, _ = task_service_components
    agent_id = "test-agent-002"
    capabilities = ["react", "frontend"]
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.find_issues_by_labels.return_value = None
    mock_github_client.get_open_issues.return_value = []

    result = task_service.request_task(agent_id, capabilities)

    assert result is None
    mock_gemini_client.select_best_issue_id.assert_not_called()
    mock_github_client.create_branch.assert_not_called()
    mock_redis_client.release_lock.assert_called_once()

def test_request_task_no_ready_issues(task_service_components):
    """Test case where open issues exist but none are ready for assignment."""
    task_service, mock_github_client, mock_redis_client, mock_gemini_client, _ = task_service_components
    agent_id = "test-agent-no-ready"
    capabilities = ["python"]
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.find_issues_by_labels.return_value = None

    mock_issue = MagicMock()
    mock_issue.body = "This issue is not ready." # Missing sections
    mock_github_client.get_open_issues.return_value = [mock_issue]

    result = task_service.request_task(agent_id, capabilities)

    assert result is None
    mock_gemini_client.select_best_issue_id.assert_not_called()
    mock_redis_client.release_lock.assert_called_once()

def test_request_task_gemini_selects_none(task_service_components):
    """Test case where Gemini returns None for the selected issue."""
    task_service, mock_github_client, mock_redis_client, mock_gemini_client, _ = task_service_components
    agent_id = "test-agent-gemini-none"
    capabilities = ["python"]
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.find_issues_by_labels.return_value = None

    mock_issue = MagicMock()
    mock_issue.body = VALID_ISSUE_BODY
    mock_github_client.get_open_issues.return_value = [mock_issue]
    mock_gemini_client.select_best_issue_id.return_value = None

    result = task_service.request_task(agent_id, capabilities)

    assert result is None
    mock_redis_client.release_lock.assert_called_once()

def test_request_task_with_previous_task(task_service_components):
    task_service, mock_github_client, mock_redis_client, mock_gemini_client, repo_name = task_service_components
    agent_id = "test-agent-003"
    capabilities = ["python"]
    previous_issue_number = 999

    mock_redis_client.acquire_lock.return_value = True
    
    mock_previous_issue = MagicMock()
    mock_previous_issue.number = previous_issue_number
    mock_github_client.find_issues_by_labels.return_value = mock_previous_issue

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

    mock_github_client.remove_label.assert_has_calls([
        call(repo_name=repo_name, issue_id=mock_previous_issue.number, label="in-progress"),
        call(repo_name=repo_name, issue_id=mock_previous_issue.number, label=agent_id)
    ], any_order=True)
    mock_github_client.add_label.assert_has_calls([
        call(repo_name=repo_name, issue_id=previous_issue_number, label="needs-review"),
        call(repo_name=repo_name, issue_id=new_mock_issue.number, label="in-progress"),
        call(repo_name=repo_name, issue_id=new_mock_issue.number, label=agent_id)
    ], any_order=True)

    assert result is not None
    assert result.issue_id == new_mock_issue.number

def test_process_previous_task_not_found(task_service_components):
    """Test that an exception during previous task processing is handled."""
    task_service, mock_github_client, _, _, repo_name = task_service_components
    agent_id = "test-agent-prev-fail"
    previous_issue_number = 998

    mock_previous_issue = MagicMock()
    mock_previous_issue.number = previous_issue_number
    mock_github_client.find_issues_by_labels.return_value = mock_previous_issue
    
    mock_github_client.remove_label.side_effect = UnknownObjectException(status=404, data={}, headers={})

    task_service._process_previous_task(agent_id)

    mock_github_client.remove_label.assert_called_once_with(
        repo_name=repo_name, issue_id=previous_issue_number, label="in-progress"
    )
    mock_github_client.add_label.assert_not_called()

def test_request_task_assign_not_found(task_service_components):
    """Test that an exception during new task assignment is handled."""
    task_service, mock_github_client, mock_redis_client, mock_gemini_client, repo_name = task_service_components
    agent_id = "test-agent-assign-fail"
    capabilities = ["python"]
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.find_issues_by_labels.return_value = None

    mock_issue = MagicMock()
    mock_issue.number = 789
    mock_issue.body = VALID_ISSUE_BODY
    mock_github_client.get_open_issues.return_value = [mock_issue]
    mock_gemini_client.select_best_issue_id.return_value = mock_issue.number

    mock_github_client.add_label.side_effect = UnknownObjectException(status=404, data={}, headers={})

    result = task_service.request_task(agent_id, capabilities)

    assert result is None
    mock_github_client.add_label.assert_called_once_with(
        repo_name=repo_name, issue_id=mock_issue.number, label="in-progress"
    )
    mock_redis_client.release_lock.assert_called_once()

def test_select_best_issue_filters_issues_without_definitions(task_service_components):
    task_service, mock_github_client, _, mock_gemini_client, _ = task_service_components

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

    mock_github_client.get_open_issues.return_value = [mock_valid_issue, mock_missing_branch]
    mock_gemini_client.select_best_issue_id.return_value = None

    task_service._select_best_issue(capabilities=["python"])

    expected_issues_for_gemini = [
        {
            "id": mock_valid_issue.number,
            "title": mock_valid_issue.title,
            "body": mock_valid_issue.body,
            "labels": []
        },
        {
            "id": mock_missing_branch.number,
            "title": mock_missing_branch.title,
            "body": mock_missing_branch.body,
            "labels": []
        }
    ]
    mock_gemini_client.select_best_issue_id.assert_called_once_with(
        expected_issues_for_gemini, ["python"]
    )

def test_request_task_lock_fails(task_service_components):
    task_service, _, mock_redis_client, _, _ = task_service_components
    mock_redis_client.acquire_lock.return_value = False

    with pytest.raises(Exception, match="Server is busy. Please try again later."):
        task_service.request_task("any-agent", [])
    
    mock_redis_client.release_lock.assert_not_called()
    
def test_parse_issue_body_normal(task_service_components):
    task_service, _, _, _, _ = task_service_components
    body = "Text before.\n\n## ブランチ名\nfeature/test-branch\n\n## 成果物\n- `file1.py`\n- `file2.py`"
    branch, deliverables = task_service._parse_issue_body(body)
    assert branch == "feature/test-branch"
    assert deliverables == "- `file1.py`\n- `file2.py`"

def test_parse_issue_body_crlf(task_service_components):
    task_service, _, _, _, _ = task_service_components
    body = "Text before.\r\n\r\n## ブランチ名\r\nfeature/crlf-branch\r\n\r\n## 成果物\r\n- `file.txt`\r\n"
    branch, deliverables = task_service._parse_issue_body(body)
    assert branch == "feature/crlf-branch"
    assert deliverables == "- `file.txt`"

def test_parse_issue_body_missing_section(task_service_components):
    task_service, _, _, _, _ = task_service_components
    body_no_branch = "## 成果物\n- `file.py`"
    branch, deliverables = task_service._parse_issue_body(body_no_branch)
    assert branch is None
    assert deliverables == "- `file.py`"

    body_no_deliverables = "## ブランチ名\nfeature/no-deliverables"
    branch, deliverables = task_service._parse_issue_body(body_no_deliverables)
    assert branch == "feature/no-deliverables"
    assert deliverables is None

def test_parse_issue_body_empty_or_none(task_service_components):
    task_service, _, _, _, _ = task_service_components
    branch, deliverables = task_service._parse_issue_body("")
    assert branch is None
    assert deliverables is None

    branch, deliverables = task_service._parse_issue_body(None)
    assert branch is None
    assert deliverables is None