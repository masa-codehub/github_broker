import subprocess
from unittest.mock import MagicMock, patch

import pytest

from sample_agent import main


@pytest.fixture
def sample_task():
    """Provides a sample task dictionary for tests."""
    return {
        "issue_id": 123,
        "title": "Test Issue",
        "prompt": "echo 'Hello World'",
    }


@pytest.mark.unit
@patch("shutil.which", return_value="/usr/bin/gemini")
@patch("subprocess.run")
@patch("sample_agent.AgentClient")
def test_main_requests_and_executes_task(
    mock_agent_client_class, mock_subprocess_run, mock_shutil_which, sample_task
):
    """Tests that the main function requests a task and executes it if one is available."""
    # Arrange
    mock_client_instance = MagicMock()
    mock_client_instance.request_task.return_value = sample_task
    mock_agent_client_class.return_value = mock_client_instance

    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["gemini", "cli", "-p", "--", "echo 'Hello World'"],
        returncode=0,
        stdout="Hello World",
        stderr="",
    )

    # Act
    main(run_once=True)

    # Assert
    mock_agent_client_class.assert_called_once()
    mock_client_instance.request_task.assert_called_once()
    mock_shutil_which.assert_called_once_with("gemini")
    mock_subprocess_run.assert_called_once_with(
        ["gemini", "cli", "-p", "--", "echo 'Hello World'"],
        text=True,
        capture_output=True,
        check=True,
    )


@pytest.mark.unit
@patch("sample_agent.AgentClient")
@patch("sample_agent.time.sleep")
def test_main_handles_no_task(mock_sleep, mock_agent_client_class):
    """Tests that the main function handles the case where no task is available."""
    # Arrange
    mock_client_instance = MagicMock()
    mock_client_instance.request_task.return_value = None
    mock_agent_client_class.return_value = mock_client_instance

    # Act
    main(run_once=True)

    # Assert
    mock_client_instance.request_task.assert_called_once()
    mock_sleep.assert_not_called()  # Because run_once=True


@pytest.mark.unit
@patch("sample_agent.AgentClient")
@patch("sample_agent.time.sleep")
def test_main_handles_exception(mock_sleep, mock_agent_client_class):
    """Tests that the main function handles exceptions during task request and logs an error."""
    # Arrange
    mock_client_instance = MagicMock()
    mock_client_instance.request_task.side_effect = Exception("Connection Error")
    mock_agent_client_class.return_value = mock_client_instance

    # Act
    with patch("logging.error") as mock_log_error:
        main(run_once=True)

    # Assert
    mock_client_instance.request_task.assert_called_once()
    mock_log_error.assert_called_once()
    assert "Connection Error" in mock_log_error.call_args[0][0]
    mock_sleep.assert_not_called()  # Because run_once=True
