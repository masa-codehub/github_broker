import pytest
from unittest.mock import patch, MagicMock
import json
import http.client
import os

from github_broker.infrastructure.agent.client import AgentClient

@pytest.fixture
def agent_client():
    """Provides a test instance of AgentClient."""
    return AgentClient(agent_id="test-agent", capabilities=["python"])

@patch('http.client.HTTPConnection')
def test_request_task_success(mock_http_connection, agent_client):
    """
    Test successful task request (200 OK).
    """
    # Arrange
    mock_conn_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.reason = "OK"
    mock_task_data = {"issue_id": 1, "title": "Test Issue"}
    mock_response.read.return_value = json.dumps(mock_task_data).encode('utf-8')
    
    mock_conn_instance.getresponse.return_value = mock_response
    mock_http_connection.return_value = mock_conn_instance

    # Act
    task = agent_client.request_task()

    # Assert
    mock_http_connection.assert_called_once_with(agent_client.host, agent_client.port)
    mock_conn_instance.request.assert_called_once()
    args, kwargs = mock_conn_instance.request.call_args
    assert args[0] == "POST"
    assert args[1] == agent_client.endpoint
    payload = json.loads(kwargs['body'])
    assert payload['agent_id'] == agent_client.agent_id
    assert payload['capabilities'] == agent_client.capabilities
    assert kwargs['headers'] == agent_client.headers
    
    assert task == mock_task_data
    mock_conn_instance.close.assert_called_once()

@patch('http.client.HTTPConnection')
def test_request_task_no_content(mock_http_connection, agent_client):
    """
    Test task request when no content is available (204 No Content).
    """
    # Arrange
    mock_conn_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 204
    mock_response.reason = "No Content"
    
    mock_conn_instance.getresponse.return_value = mock_response
    mock_http_connection.return_value = mock_conn_instance

    # Act
    task = agent_client.request_task()

    # Assert
    assert task is None
    mock_conn_instance.close.assert_called_once()

@patch('http.client.HTTPConnection')
def test_request_task_server_error(mock_http_connection, agent_client):
    """
    Test task request when the server returns an error (e.g., 500).
    """
    # Arrange
    mock_conn_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 500
    mock_response.reason = "Internal Server Error"
    mock_response.read.return_value = b'{"error": "Something went wrong"}'
    
    mock_conn_instance.getresponse.return_value = mock_response
    mock_http_connection.return_value = mock_conn_instance

    # Act
    task = agent_client.request_task()

    # Assert
    assert task is None
    mock_conn_instance.close.assert_called_once()

@patch('http.client.HTTPConnection', side_effect=ConnectionRefusedError("Connection refused"))
def test_request_task_connection_error(mock_http_connection, agent_client):
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

def test_agent_client_initialization_default_port():
    """
    Test AgentClient initialization with the default port when env var is not set.
    """
    if "APP_PORT" in os.environ:
        del os.environ["APP_PORT"]
    client = AgentClient(agent_id="test", capabilities=[])
    assert client.port == 8080
