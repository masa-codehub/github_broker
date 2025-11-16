from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from broker_main import app
from github_broker.interface.api import get_task_service


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def mock_task_service() -> Generator[None, None, None]:
    """Override the dependency to avoid running the actual service."""
    app.dependency_overrides[get_task_service] = lambda: None
    yield
    del app.dependency_overrides[get_task_service]


@pytest.mark.unit
def test_health_check(client: TestClient):
    """Tests the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.unit
def test_request_task_endpoint_stub(client: TestClient, mock_task_service: None):
    """
    Tests that the /request-task endpoint returns 204 No Content
    as it is currently stubbed.
    """
    # Arrange
    request_body = {"agent_id": "test-agent"}

    # Act
    response = client.post("/request-task", json=request_body)

    # Assert
    assert response.status_code == 204


@pytest.mark.unit
def test_create_fix_task_endpoint_stub(client: TestClient, mock_task_service: None):
    """
    Tests that the /tasks/fix endpoint returns the stubbed message.
    """
    # Arrange
    request_body = {
        "pull_request_number": 123,
        "review_comments": ["This needs a fix."],
    }

    # Act
    response = client.post("/tasks/fix", json=request_body)

    # Assert
    assert response.status_code == 202
    assert response.json() == {"message": "Fix task creation has been accepted (stubbed)."}
