import os
import subprocess
from unittest.mock import MagicMock, mock_open, patch

import pytest

from agents_main import ERROR_SLEEP_SECONDS, NO_TASK_SLEEP_SECONDS, main

# テスト全体で利用するコマンドの定数
GEMINI_COMMAND = "cat context.md | gemini --model gemini-2.5-flash --yolo"


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


@patch("agents_main.logging.info")
@patch("agents_main.subprocess.run")
@patch("agents_main.shutil.which")
@patch("agents_main.AgentClient")
def test_main_no_task_assigned(
    mock_agent_client,
    mock_shutil_which,
    mock_subprocess_run,
    mock_logging_info,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    mock_agent_client.return_value.request_task.return_value = None  # タスクなし
    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()
    mock_subprocess_run.assert_not_called()
    expected_log_message = f"利用可能なタスクがありません。{NO_TASK_SLEEP_SECONDS // 60}分後に再試行します。"
    mock_logging_info.assert_any_call(expected_log_message)


@patch("builtins.open", new_callable=mock_open)
@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
def test_main_task_assigned_with_prompt(
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
    mock_file_open,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    prompt_content = "test prompt content"
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": prompt_content,
    }
    mock_subprocess_run.return_value = MagicMock(stdout="cli output", stderr="")

    main(run_once=True)

    mock_agent_client.return_value.request_task.assert_called_once()

    # Verify context.md was written correctly
    mock_file_open.assert_called_once_with("context.md", "w", encoding="utf-8")
    mock_file_open().write.assert_called_once_with(prompt_content.strip())

    # Verify subprocess was called correctly
    mock_subprocess_run.assert_called_once_with(
        GEMINI_COMMAND,
        text=True,
        capture_output=True,
        check=True,
        shell=True,
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


@patch("agents_main.logging.error")
@patch("agents_main.subprocess.run")
@patch("agents_main.shutil.which")
@patch("agents_main.AgentClient")
def test_main_exception_handling(
    mock_agent_client,
    mock_shutil_which,
    mock_subprocess_run,
    mock_logging_error,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    mock_agent_client.return_value.request_task.side_effect = Exception("Test Error")

    main(run_once=True)

    mock_agent_client.return_value.request_task.assert_called_once()
    expected_log_message = f"エラーが発生しました: Test Error。{ERROR_SLEEP_SECONDS // 60}分後に再試行します..."
    mock_logging_error.assert_called_with(expected_log_message)
    mock_subprocess_run.assert_not_called()


@patch("builtins.open", new_callable=mock_open)
@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
def test_main_prompt_sanitization_removes_null_bytes(
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
    mock_file_open,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    malicious_prompt = "test\n\r\x00prompt\x00 with nulls"
    expected_safe_prompt = "test\n\rprompt with nulls"
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": malicious_prompt,
    }
    mock_subprocess_run.return_value = MagicMock(stdout="cli output", stderr="")

    main(run_once=True)

    # Verify context.md was written correctly
    mock_file_open.assert_called_once_with("context.md", "w", encoding="utf-8")
    mock_file_open().write.assert_called_once_with(expected_safe_prompt.strip())

    mock_subprocess_run.assert_called_once_with(
        GEMINI_COMMAND,
        text=True,
        capture_output=True,
        check=True,
        shell=True,
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
        returncode=1, cmd=GEMINI_COMMAND, output="", stderr="cli error"
    )

    main(run_once=True)

    mock_logging_error.assert_any_call(
        f"gemini cli の実行中にエラーが発生しました: Command '{GEMINI_COMMAND}' returned non-zero exit status 1."
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
