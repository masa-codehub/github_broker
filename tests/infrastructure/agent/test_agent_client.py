import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest
import requests

from github_broker import AgentClient


@pytest.fixture
def agent_client():
    """AgentClientのテストインスタンスを提供します。"""
    return AgentClient(agent_id="test-agent", agent_role="BACKENDCODER")


@pytest.mark.unit
@patch("subprocess.run")
@patch("requests.post")
def test_request_task_success(mock_post, mock_subprocess_run, agent_client):
    """
    タスクリクエストが成功し、プロンプトが実行されるケース（200 OK）をテストします。
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_task_data = {
        "issue_id": 1,
        "title": "Test Issue",
        "prompt": "echo 'Hello World'",
    }
    mock_response.json.return_value = mock_task_data
    mock_post.return_value = mock_response

    mock_subprocess_run.return_value = MagicMock(
        stdout="Hello World", stderr="", returncode=0
    )

    # Act
    task = agent_client.request_task()

    # Assert
    expected_url = (
        f"http://{agent_client.host}:{agent_client.port}{agent_client.endpoint}"
    )
    expected_payload = {
        "agent_id": agent_client.agent_id,
        "agent_role": agent_client.agent_role,
    }
    mock_post.assert_called_once_with(
        expected_url, json=expected_payload, headers=agent_client.headers, timeout=120
    )
    mock_response.raise_for_status.assert_called_once()
    assert task == mock_task_data
    mock_subprocess_run.assert_called_once_with(
        mock_task_data["prompt"],
        shell=True,
        check=True,
        text=True,
        capture_output=True,
    )


@pytest.mark.unit
@patch("subprocess.run")
@patch("requests.post")
def test_request_task_prompt_execution_failure(
    mock_post, mock_subprocess_run, agent_client
):
    """
    プロンプトの実行が失敗するケースをテストします。
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_task_data = {
        "issue_id": 1,
        "title": "Test Issue",
        "prompt": "exit 1",  # 失敗するコマンドを想定
    }
    mock_response.json.return_value = mock_task_data
    mock_post.return_value = mock_response

    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=mock_task_data["prompt"], stderr="Command failed"
    )

    # Act
    task = agent_client.request_task()

    # Assert
    assert task is None
    mock_subprocess_run.assert_called_once_with(
        mock_task_data["prompt"],
        shell=True,
        check=True,
        text=True,
        capture_output=True,
    )


@pytest.mark.unit
@patch("requests.post")
def test_request_task_with_custom_timeout(mock_post, agent_client):
    """
    カスタムタイムアウト値を使用してタスクリクエストが成功するケースをテストします。
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"issue_id": 2, "title": "Custom Timeout Test"}
    mock_post.return_value = mock_response
    custom_timeout = 60

    # Act
    agent_client.request_task(timeout=custom_timeout)

    # Assert
    expected_url = (
        f"http://{agent_client.host}:{agent_client.port}{agent_client.endpoint}"
    )
    expected_payload = {
        "agent_id": agent_client.agent_id,
        "agent_role": agent_client.agent_role,
    }
    mock_post.assert_called_once_with(
        expected_url,
        json=expected_payload,
        headers=agent_client.headers,
        timeout=custom_timeout,
    )


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
    client = AgentClient(agent_id="test", agent_role="", host="testhost", port=9000)
    assert client.port == 9000


@pytest.mark.unit
@patch.dict(os.environ, {"BROKER_PORT": "9999"})
def test_agent_client_initialization_with_env_var():
    """
    BROKER_PORT環境変数を使用してAgentClientが初期化されることをテストします。
    """
    client = AgentClient(agent_id="test", agent_role="")
    assert client.port == 9999


@pytest.mark.unit
def test_agent_client_initialization_default_port(monkeypatch):
    """
    環境変数が設定されていない場合に、AgentClientがデフォルトポートで初期化されることをテストします。
    """
    monkeypatch.delenv("BROKER_PORT", raising=False)
    client = AgentClient(agent_id="test", agent_role="")
    assert client.port == 8080
