import pytest
from unittest.mock import patch, MagicMock
import os
import requests

from github_broker import AgentClient

@pytest.fixture
def agent_client():
    """Provides a test instance of AgentClient."""
    return AgentClient(agent_id="test-agent", capabilities=["python"])

@patch('requests.post')
def test_request_task_success(mock_post, agent_client):
    """
    Test successful task request (200 OK).
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_task_data = {"issue_id": 1, "title": "Test Issue"}
    mock_response.json.return_value = mock_task_data
    mock_post.return_value = mock_response

    # Act
    task = agent_client.request_task()

    # Assert
    expected_url = f"http://{agent_client.host}:{agent_client.port}{agent_client.endpoint}"
    expected_payload = {
        "agent_id": agent_client.agent_id,
        "capabilities": agent_client.capabilities
    }
    mock_post.assert_called_once_with(
        expected_url,
        json=expected_payload,
        headers=agent_client.headers,
        timeout=30
    )
    mock_response.raise_for_status.assert_called_once()
    assert task == mock_task_data

@patch('requests.post')
def test_request_task_no_content(mock_post, agent_client):
    """
    Test task request when no content is available (204 No Content).
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    # Act
    task = agent_client.request_task()

    # Assert
    assert task is None
    mock_response.raise_for_status.assert_not_called()

@patch('requests.post')
def test_request_task_server_error(mock_post, agent_client):
    """
    Test task request when the server returns an error that raises an exception.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server Error")
    mock_post.return_value = mock_response

    # Act
    task = agent_client.request_task()

    # Assert
    assert task is None

@patch('requests.post', side_effect=requests.exceptions.ConnectionError("Connection refused"))
def test_request_task_connection_error(mock_post, agent_client):
    """
    Test task request when a connection error occurs.
    """
    # Act
    task = agent_client.request_task()

    # Assert
    assert task is None

def test_agent_client_initialization_with_port():
    """
    Test AgentClient initialization with a specific port.
    """
    client = AgentClient(agent_id="test", capabilities=[], host="testhost", port=9000)
    assert client.port == 9000

@patch.dict(os.environ, {"APP_PORT": "9999"})
def test_agent_client_initialization_with_env_var():
    """
    Test AgentClient initialization using APP_PORT environment variable.
    """
    client = AgentClient(agent_id="test", capabilities=[])
    assert client.port == 9999

def test_agent_client_initialization_default_port(monkeypatch):
    """
    Test AgentClient initialization with the default port when env var is not set.
    """
    monkeypatch.delenv("APP_PORT", raising=False)
    client = AgentClient(agent_id="test", capabilities=[])
    assert client.port == 8080