
import pytest
from unittest.mock import MagicMock

from github_broker.application.task_service import TaskService
from github_broker.interface.models import TaskResponse

# pytest.fixtureは、複数のテストで再利用可能なコンポーネント（この場合はテスト対象のサービスとモック）
# を作成するためのデコレータです。
@pytest.fixture
def task_service_components():
    """Set up mock clients and TaskService instance for tests."""
    mock_github_client = MagicMock()
    mock_redis_client = MagicMock()
    repo_name = "test/repo"
    task_service = TaskService(
        github_client=mock_github_client,
        redis_client=mock_redis_client,
        repo_name=repo_name
    )
    # テストで使えるように、複数のオブジェクトをタプルで返す
    return task_service, mock_github_client, mock_redis_client, repo_name

# テスト関数は、引数としてfixtureを受け取ることができます。
def test_request_task_success_first_task(task_service_components):
    """
    Test the successful assignment of a task to an agent with no previous task.
    """
    # Arrange
    # fixtureからコンポーネントを展開
    task_service, mock_github_client, mock_redis_client, repo_name = task_service_components
    agent_id = "test-agent-001"
    capabilities = ["python", "fastapi"]

    # --- Mock Redis Client responses ---
    mock_redis_client.acquire_lock.return_value = True
    mock_redis_client.get_assignment.return_value = None # No previous task

    # --- Mock GitHub Client responses ---
    mock_issue = MagicMock()
    mock_issue.id = 123
    mock_issue.number = 123
    mock_issue.title = "Fix the bug"
    mock_issue.body = "There is a bug that needs fixing."
    mock_label = MagicMock()
    mock_label.name = "bug"
    mock_issue.labels = [mock_label]
    mock_issue.html_url = "https://github.com/test/repo/issues/123"
    mock_github_client.get_open_issues.return_value = [mock_issue]
    mock_github_client.create_branch.return_value = True

    # Act
    result = task_service.request_task(agent_id, capabilities)

    # Assert
    # --- Verify lock handling ---
    mock_redis_client.acquire_lock.assert_called_once()
    mock_redis_client.release_lock.assert_called_once()

    # --- Verify previous task handling ---
    mock_redis_client.get_assignment.assert_called_once_with(agent_id)
    # No previous task, so label should not be updated
    mock_github_client.update_issue_label.assert_not_called()

    # --- Verify new task assignment ---
    mock_github_client.get_open_issues.assert_called_once()
    
    # --- Verify branch creation ---
    expected_branch_name = f"feature/issue-{mock_issue.id}"
    mock_github_client.create_branch.assert_called_once_with(
        repo_name=repo_name,
        branch_name=expected_branch_name
    )

    # --- Verify ledger update ---
    mock_redis_client.set_assignment.assert_called_once_with(agent_id, mock_issue.id)

    # --- Verify response ---
    assert isinstance(result, TaskResponse)
    assert result.issue_id == mock_issue.id
    assert result.title == mock_issue.title
    assert result.branch_name == expected_branch_name

def test_request_task_no_issues_available(task_service_components):
    """
    Test that no task is assigned when no open issues are available.
    """
    # Arrange
    task_service, mock_github_client, mock_redis_client, _ = task_service_components
    agent_id = "test-agent-002"
    capabilities = ["react", "frontend"]
    mock_redis_client.acquire_lock.return_value = True
    mock_redis_client.get_assignment.return_value = None
    mock_github_client.get_open_issues.return_value = [] # No issues

    # Act
    result = task_service.request_task(agent_id, capabilities)

    # Assert
    assert result is None
    mock_redis_client.acquire_lock.assert_called_once()
    mock_github_client.get_open_issues.assert_called_once()
    # Should not proceed to create branch or assign task
    mock_github_client.create_branch.assert_not_called()
    mock_redis_client.set_assignment.assert_not_called()
    # Lock should always be released
    mock_redis_client.release_lock.assert_called_once()

def test_request_task_with_previous_task(task_service_components):
    """
    Test that a previous task is marked as complete before assigning a new one.
    """
    # Arrange
    task_service, mock_github_client, mock_redis_client, repo_name = task_service_components
    agent_id = "test-agent-003"
    capabilities = ["python"]
    previous_issue_id = 999

    mock_redis_client.acquire_lock.return_value = True
    mock_redis_client.get_assignment.return_value = previous_issue_id

    # Mock for the new issue to be assigned
    new_mock_issue = MagicMock()
    new_mock_issue.id = 124
    new_mock_issue.number = 124
    new_mock_issue.title = "A new task"
    new_mock_issue.body = "Details for the new task."
    new_mock_issue.labels = []
    new_mock_issue.html_url = "https://github.com/test/repo/issues/124"
    mock_github_client.get_open_issues.return_value = [new_mock_issue]

    # Act
    result = task_service.request_task(agent_id, capabilities)

    # Assert
    # --- Verify previous task handling ---
    mock_redis_client.get_assignment.assert_called_once_with(agent_id)
    mock_github_client.update_issue_label.assert_called_once_with(
        repo_name=repo_name,
        issue_id=previous_issue_id,
        new_label="needs-review"
    )

    # --- Verify new task assignment is still correct ---
    assert result is not None
    assert result.issue_id == new_mock_issue.id
    mock_redis_client.set_assignment.assert_called_once_with(agent_id, new_mock_issue.id)
    mock_github_client.create_branch.assert_called_once()
    mock_redis_client.release_lock.assert_called_once()

def test_request_task_lock_fails(task_service_components):
    """
    Test that an exception is raised if the lock cannot be acquired.
    """
    # Arrange
    task_service, mock_github_client, mock_redis_client, _ = task_service_components
    agent_id = "test-agent-004"
    capabilities = ["*"]
    mock_redis_client.acquire_lock.return_value = False

    # Act & Assert
    # pytest.raisesは、特定の例外が発生することを検証します。
    with pytest.raises(Exception, match="Server is busy. Please try again later."):
        task_service.request_task(agent_id, capabilities)

    # Verify that no other operations were attempted
    mock_redis_client.get_assignment.assert_not_called()
    mock_github_client.get_open_issues.assert_not_called()
    mock_redis_client.release_lock.assert_not_called()
