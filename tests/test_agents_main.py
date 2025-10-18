import os
import subprocess
from unittest.mock import mock_open, patch

import pytest

from agents_main import (
    ERROR_SLEEP_SECONDS,
    NO_TASK_SLEEP_SECONDS,
    SUCCESS_SLEEP_SECONDS,
    main,
)


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
@patch("agents_main.subprocess.run")
@patch("agents_main.logging.info")
def test_main_no_task_assigned(
    mock_logging_info,
    mock_subprocess_run,
    mock_agent_client,
):
    mock_agent_client.return_value.request_task.return_value = None
    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()
    mock_subprocess_run.assert_not_called()
    expected_log_message = f"利用可能なタスクがありません。{NO_TASK_SLEEP_SECONDS // 60}分後に再試行します。"
    mock_logging_info.assert_any_call(expected_log_message)


@patch("agents_main.subprocess.run")
@patch("agents_main.AgentClient")
@patch("builtins.open", new_callable=mock_open)
@pytest.mark.parametrize(
    "task_type, required_role, expected_model",
    [
        ("development", "BACKENDCODER", "gemini-2.5-flash"),
        ("review", "CODE_REVIEWER", "gemini-2.5-pro"),
        (None, "BACKENDCODER", "gemini-2.5-flash"),
    ],
    ids=["development", "review", "default"],
)
def test_main_task_assigned_dynamic_logic(
    mock_file_open,
    mock_agent_client,
    mock_subprocess_run,
    task_type,
    required_role,
    expected_model,
):
    prompt_content = "test prompt content"

    return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": prompt_content,
        "required_role": required_role,
    }
    if task_type is not None:
        return_value["task_type"] = task_type

    mock_agent_client.return_value.request_task.return_value = return_value
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["dummy"], returncode=0, stdout="cli output", stderr=""
    )

    main(run_once=True)

    mock_agent_client.return_value.request_task.assert_called_once()

    expected_update_args = ["bash", ".build/update_gemini_context.sh"]
    expected_env = os.environ.copy()
    expected_env["AGENT_ROLE"] = required_role
    call_args_list = mock_subprocess_run.call_args_list

    assert call_args_list[0].args[0] == expected_update_args
    assert call_args_list[0].kwargs["check"] is True
    assert call_args_list[0].kwargs["env"] == expected_env
    assert "shell" not in call_args_list[0].kwargs

    expected_gemini_command = f"cat context.md | gemini --model {expected_model} --yolo"
    assert call_args_list[1].args[0] == expected_gemini_command
    assert call_args_list[1].kwargs["check"] is True
    assert call_args_list[1].kwargs["shell"] is True

    assert mock_subprocess_run.call_count == 2
    mock_file_open.assert_called_once_with("context.md", "w", encoding="utf-8")
    mock_file_open().write.assert_called_once_with(prompt_content.strip())


@patch("agents_main.subprocess.run")
@patch("agents_main.AgentClient")
def test_main_task_assigned_without_prompt(
    mock_agent_client,
    mock_subprocess_run,
):
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": None,
    }
    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()
    mock_subprocess_run.assert_not_called()


@patch("agents_main.AgentClient")
@patch("agents_main.subprocess.run")
@patch("agents_main.logging.error")
def test_main_exception_handling(
    mock_logging_error,
    mock_subprocess_run,
    mock_agent_client,
):
    mock_agent_client.return_value.request_task.side_effect = Exception("Test Error")
    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()
    expected_log_message = f"エラーが発生しました: Test Error。{ERROR_SLEEP_SECONDS // 60}分後に再試行します..."
    mock_logging_error.assert_called_with(expected_log_message)
    mock_subprocess_run.assert_not_called()


@patch("agents_main.subprocess.run")
@patch("agents_main.AgentClient")
@patch("builtins.open", new_callable=mock_open)
def test_main_prompt_sanitization_removes_null_bytes(
    mock_file_open,
    mock_agent_client,
    mock_subprocess_run,
):
    malicious_prompt = "test\n\r\x00prompt\x00 with nulls"
    expected_safe_prompt = "test\n\rprompt with nulls"
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": malicious_prompt,
        "required_role": "BACKENDCODER",
    }
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["dummy command"], returncode=0, stdout="cli output", stderr=""
    )
    main(run_once=True)
    mock_file_open.assert_called_once_with("context.md", "w", encoding="utf-8")
    mock_file_open().write.assert_called_once_with(expected_safe_prompt.strip())


@patch("agents_main.AgentClient")
@patch("agents_main.subprocess.run")
@patch("agents_main.logging.error")
def test_main_subprocess_called_process_error(
    mock_logging_error,
    mock_subprocess_run,
    mock_agent_client,
):
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": "test prompt",
        "required_role": "BACKENDCODER",
    }
    expected_gemini_command = "cat context.md | gemini --model gemini-2.5-flash --yolo"
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=expected_gemini_command,
        output="cli output",
        stderr="cli error",
    )

    main(run_once=True)

    # エラーメッセージをより柔軟にチェック
    error_calls = [str(call) for call in mock_logging_error.call_args_list]
    expected_main_error_msg = (
        f"コマンド '{expected_gemini_command}' の実行中にエラーが発生しました"
    )
    assert any(expected_main_error_msg in call for call in error_calls)
    assert any("stdout: cli output" in call for call in error_calls)
    assert any("stderr: cli error" in call for call in error_calls)


@patch("agents_main.subprocess.run")
@patch("agents_main.AgentClient")
def test_main_run_once_true_exits_after_task(
    mock_agent_client,
    mock_subprocess_run,
):
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": "test prompt",
    }
    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()


@patch("agents_main.subprocess.run")
@patch("agents_main.AgentClient")
def test_main_run_once_true_exits_no_task(
    mock_agent_client,
    mock_subprocess_run,
):
    mock_agent_client.return_value.request_task.return_value = None
    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()


@patch("agents_main.subprocess.run")
@patch("agents_main.AgentClient")
def test_main_run_once_true_exits_on_exception(
    mock_agent_client,
    mock_subprocess_run,
):
    mock_agent_client.return_value.request_task.side_effect = Exception("Test Error")
    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()


@patch("agents_main.subprocess.run")
@patch("agents_main.AgentClient")
@patch("agents_main.time.sleep")
@pytest.mark.parametrize(
    "task_result, expected_sleep_seconds",
    [
        (
            {"issue_id": 1, "title": "Test Task", "prompt": "test prompt"},
            SUCCESS_SLEEP_SECONDS,
        ),
        (None, NO_TASK_SLEEP_SECONDS),
        (Exception("Test Error"), ERROR_SLEEP_SECONDS),
    ],
    ids=["success", "no_task", "error"],
)
def test_main_calls_sleep_in_loop(
    mock_sleep,
    mock_agent_client,
    mock_subprocess_run,
    task_result,
    expected_sleep_seconds,
):
    if isinstance(task_result, Exception):
        mock_agent_client.return_value.request_task.side_effect = task_result
    else:
        mock_agent_client.return_value.request_task.return_value = task_result

    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["gemini"], returncode=0, stdout="cli output", stderr=""
    )
    mock_sleep.side_effect = SystemExit
    with pytest.raises(SystemExit):
        main(run_once=False)
    mock_sleep.assert_called_once_with(expected_sleep_seconds)
