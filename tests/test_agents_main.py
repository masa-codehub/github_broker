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
@pytest.mark.parametrize(
    "task_type, required_role, expected_model",
    [
        ("development", "BACKENDCODER", "gemini-2.5-flash"),
        ("review", "CODE_REVIEWER", "gemini-2.5-pro"),
        (
            None,
            "BACKENDCODER",
            "gemini-2.5-flash",
        ),  # Default case (None -> development)
    ],
    ids=["development", "review", "default"],
)
def test_main_task_assigned_dynamic_logic(
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
    mock_file_open,
    task_type,
    required_role,
    expected_model,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    prompt_content = "test prompt content"

    # request_taskの戻り値を設定
    return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": prompt_content,
        "required_role": required_role,
    }
    if task_type is not None:
        return_value["task_type"] = task_type

    mock_agent_client.return_value.request_task.return_value = return_value

    # subprocess.runのモックを調整し、2回の呼び出しを検証できるようにする
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["dummy"], returncode=0, stdout="cli output", stderr=""
    )

    main(run_once=True)

    mock_agent_client.return_value.request_task.assert_called_once()

    # 1. コンテキスト更新スクリプトの実行検証
    expected_update_args = ["/app/.build/update_gemini_context.sh"]
    expected_env = os.environ.copy()
    expected_env["AGENT_ROLE"] = required_role

    # 呼び出しの引数を検証するために、call_args_listを使用
    call_args_list = mock_subprocess_run.call_args_list

    # 最初の呼び出しがupdate_gemini_context.shであることを検証
    assert call_args_list[0].args[0] == expected_update_args
    assert call_args_list[0].kwargs["check"] is True
    assert call_args_list[0].kwargs["env"] == expected_env
    assert "shell" not in call_args_list[0].kwargs

    # 2. gemini CLIの実行検証
    expected_gemini_command = f"cat context.md | gemini --model {expected_model} --yolo"

    # 2番目の呼び出しがgemini CLIであることを検証
    assert call_args_list[1].args[0] == expected_gemini_command
    assert call_args_list[1].kwargs["check"] is True
    assert call_args_list[1].kwargs["shell"] is True

    # 呼び出し回数が2回であることを確認
    assert mock_subprocess_run.call_count == 2

    # Verify context.md was written correctly
    mock_file_open.assert_called_once_with("context.md", "w", encoding="utf-8")
    mock_file_open().write.assert_called_once_with(prompt_content.strip())


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
        "required_role": "BACKENDCODER",
    }
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["dummy command"], returncode=0, stdout="cli output", stderr=""
    )

    main(run_once=True)

    # Verify context.md was written correctly
    mock_file_open.assert_called_once_with("context.md", "w", encoding="utf-8")
    mock_file_open().write.assert_called_once_with(expected_safe_prompt.strip())


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
        "required_role": "BACKENDCODER",
    }

    # 最初の呼び出し（update_gemini_context.sh）は成功させる
    # 2回目の呼び出し（gemini CLI）でエラーを発生させる
    def side_effect_func(*args, **kwargs):
        if args[0] == ["/app/.build/update_gemini_context.sh"]:
            return subprocess.CompletedProcess(
                args=["dummy"], returncode=0, stdout="", stderr=""
            )
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd="cat context.md | gemini --model gemini-2.5-flash --yolo",
            output="",
            stderr="cli error",
        )

    mock_subprocess_run.side_effect = side_effect_func

    main(run_once=True)

    # エラーログの検証
    expected_gemini_command = "cat context.md | gemini --model gemini-2.5-flash --yolo"
    mock_logging_error.assert_any_call(
        f"コマンド '{expected_gemini_command}' の実行中にエラーが発生しました: Command '{expected_gemini_command}' returned non-zero exit status 1."
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
@patch("agents_main.time.sleep")
@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
def test_main_calls_sleep_in_loop(
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
    mock_sleep,
    task_result,
    expected_sleep_seconds,
):
    mock_shutil_which.return_value = "/usr/bin/gemini"
    if isinstance(task_result, Exception):
        mock_agent_client.return_value.request_task.side_effect = task_result
    else:
        mock_agent_client.return_value.request_task.return_value = task_result

    # モックの改善: MagicMock -> subprocess.CompletedProcess
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["gemini"], returncode=0, stdout="cli output", stderr=""
    )
    mock_sleep.side_effect = SystemExit  # sleepが呼ばれたら終了

    with pytest.raises(SystemExit):
        main(run_once=False)

    mock_sleep.assert_called_once_with(expected_sleep_seconds)
