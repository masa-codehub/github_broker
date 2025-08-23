from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from github_broker.application.exceptions import LockAcquisitionError
from github_broker.application.task_service import TaskService
from github_broker.interface.api import app, get_task_service
from github_broker.interface.models import TaskResponse

client = TestClient(app)


def test_request_task_success():
    """Test a successful task request to the /request-task endpoint."""
    # Arrange
    mock_task_service = MagicMock(spec=TaskService)
    expected_task = TaskResponse(
        issue_id=123,
        issue_url="http://example.com/issue/123",
        title="Test Issue",
        body="This is a test issue.",
        labels=["bug"],
        branch_name="feature/issue-123-test",
    )
    mock_task_service.request_task.return_value = expected_task

    # Override the dependency using FastAPI's dependency_overrides
    app.dependency_overrides[get_task_service] = lambda: mock_task_service

    # Act
    response = client.post(
        "/request-task",
        json={"agent_id": "test-agent", "capabilities": ["python"]},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_task.model_dump(mode="json")
    mock_task_service.request_task.assert_called_once_with(agent_id="test-agent")

    # Clean up the override after the test
    del app.dependency_overrides[get_task_service]


def test_request_task_no_task_available():
    """Test the /request-task endpoint when no task is available (204 No Content)."""
    # Arrange
    mock_task_service = MagicMock(spec=TaskService)
    mock_task_service.request_task.return_value = None

    # Override the dependency
    app.dependency_overrides[get_task_service] = lambda: mock_task_service

    # Act
    response = client.post(
        "/request-task",
        json={"agent_id": "test-agent", "capabilities": ["python"]},
    )

    # Assert
    assert response.status_code == 204
    mock_task_service.request_task.assert_called_once_with(agent_id="test-agent")

    # Clean up
    del app.dependency_overrides[get_task_service]


def test_request_task_lock_error():
    """Test the /request-task endpoint when a LockAcquisitionError is raised."""
    # Arrange
    mock_task_service = MagicMock(spec=TaskService)
    error_message = "Server is busy. Please try again later."
    mock_task_service.request_task.side_effect = LockAcquisitionError(error_message)

    # Override the dependency
    app.dependency_overrides[get_task_service] = lambda: mock_task_service

    # Act
    response = client.post(
        "/request-task",
        json={"agent_id": "test-agent", "capabilities": ["python"]},
    )

    # Assert
    assert response.status_code == 503
    assert response.json() == {"message": error_message}
    mock_task_service.request_task.assert_called_once_with(agent_id="test-agent")

    # Clean up
    del app.dependency_overrides[get_task_service]
