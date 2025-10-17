import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from github_broker import AgentClient


@pytest.fixture
def agent_client():
    """AgentClientのテストインスタンスを提供します。"""
    return AgentClient(agent_id="test-agent")


@pytest.mark.unit
@patch("requests.post")
def test_request_task_no_content(mock_post, agent_client):
    """
    利用可能なコンテンツがない場合（204 No Content）のタスクリクエストをテストします。
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


@pytest.mark.unit
@patch("requests.post")
def test_request_task_server_error(mock_post, agent_client):
    """
    サーバーが例外を発生させるエラーを返した場合のタスクリクエストをテストします。
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Server Error"
    )
    mock_post.return_value = mock_response

    # Act
    task = agent_client.request_task()

    # Assert
    assert task is None


@pytest.mark.unit
@patch(
    "requests.post",
    side_effect=requests.exceptions.ConnectionError("Connection refused"),
)
def test_request_task_connection_error(mock_post, agent_client):
    """
    接続エラーが発生した場合のタスクリクエストをテストします。
    """
    # Act
    task = agent_client.request_task()

    # Assert
    assert task is None


@pytest.mark.unit
def test_agent_client_initialization_with_port():
    """
    特定のポートでAgentClientが初期化されることをテストします。
    """
    client = AgentClient(agent_id="test", host="testhost", port=9000)
    assert client.port == 9000


@pytest.mark.unit
@patch.dict(os.environ, {"BROKER_PORT": "9999"})
def test_agent_client_initialization_with_env_var():
    """
    BROKER_PORT環境変数を使用してAgentClientが初期化されることをテストします。
    """
    client = AgentClient(agent_id="test")
    assert client.port == 9999


@pytest.mark.unit
def test_agent_client_initialization_default_port(monkeypatch):
    """
    環境変数が設定されていない場合に、AgentClientがデフォルトポートで初期化されることをテストします。
    """
    monkeypatch.delenv("BROKER_PORT", raising=False)
    client = AgentClient(agent_id="test")
    assert client.port == 8080
