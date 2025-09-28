import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from agents_main import main


@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(
        os.environ,
        {
            "AGENT_NAME": "test-agent",
            "BROKER_HOST": "test-host",
            "BROKER_PORT": "1234",
            "AGENT_ROLE": "TESTER",
        },
    ):
        yield


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
@patch("agents_main.logging.error")
def test_main_gemini_command_not_found(
    mock_logging_error,
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
):
    mock_shutil_which.return_value = None  # geminiコマンドが見つからない
    main(run_once=True)
    mock_logging_error.assert_called_with(
        "'gemini' command not found. Please ensure it is installed and in your PATH."
    )
    mock_agent_client.assert_not_called()
    mock_subprocess_run.assert_not_called()


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
def test_main_no_task_assigned(
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    mock_agent_client.return_value.request_task.return_value = None  # タスクなし
    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()
    mock_subprocess_run.assert_not_called()


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
def test_main_task_assigned_with_prompt(
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": "test prompt content",
    }
    mock_subprocess_run.return_value = MagicMock(stdout="cli output", stderr="")

    main(run_once=True)

    mock_agent_client.return_value.request_task.assert_called_once()
    mock_subprocess_run.assert_called_once_with(
        ["gemini", "cli", "-p", "--", "test prompt content"],
        text=True,
        capture_output=True,
        check=True,
    )


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
def test_main_task_assigned_without_prompt(
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": None,
    }

    main(run_once=True)

    mock_agent_client.return_value.request_task.assert_called_once()
    mock_subprocess_run.assert_not_called()


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
@patch("agents_main.logging.error")
def test_main_exception_handling(
    mock_logging_error,
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    mock_agent_client.return_value.request_task.side_effect = Exception("Test Error")

    main(run_once=True)

    mock_agent_client.return_value.request_task.assert_called_once()
    mock_logging_error.assert_called_with(
        "エラーが発生しました: Test Error。60分後に再試行します..."
    )
    mock_subprocess_run.assert_not_called()


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
@patch("agents_main.logging.warning")
def test_main_prompt_sanitization(
    mock_logging_warning,
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    malicious_prompt = "test\n\r\x00prompt; rm -rf /"
    expected_safe_prompt = "test prompt; rm -rf /"
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": malicious_prompt,
    }
    mock_subprocess_run.return_value = MagicMock(stdout="cli output", stderr="")

    main(run_once=True)

    mock_subprocess_run.assert_called_once_with(
        ["gemini", "cli", "-p", "--", expected_safe_prompt],
        text=True,
        capture_output=True,
        check=True,
    )


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
@patch("agents_main.logging.error")
def test_main_subprocess_called_process_error(
    mock_logging_error,
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": "test prompt",
    }
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd="gemini cli", output="", stderr="cli error"
    )

    main(run_once=True)

    mock_logging_error.assert_any_call(
        "gemini cli の実行中にエラーが発生しました: Command 'gemini cli' returned non-zero exit status 1."
    )
    mock_logging_error.assert_any_call("stdout: ")
    mock_logging_error.assert_any_call("stderr: cli error")


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
def test_main_run_once_true_exits_after_task(
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": "test prompt",
    }
    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
def test_main_run_once_true_exits_no_task(
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    mock_agent_client.return_value.request_task.return_value = None
    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
def test_main_run_once_true_exits_on_exception(
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    mock_agent_client.return_value.request_task.side_effect = Exception("Test Error")
    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()
