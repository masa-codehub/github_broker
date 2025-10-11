import os
import subprocess
from unittest.mock import ANY, MagicMock, call, mock_open, patch

import pytest

from agents_main import main

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


@patch("builtins.open", new_callable=mock_open)
@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
@patch("agents_main.os.path.isfile", return_value=True)
@patch("agents_main.os.access", return_value=True)
def test_main_task_assigned_with_prompt(
    mock_os_access,
    mock_os_path_isfile,
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

    # 2回の呼び出しをモック
    mock_subprocess_run.side_effect = [
        MagicMock(
            stdout="script output", stderr=""
        ),  # 1回目: _run_update_context_script
        MagicMock(stdout="cli output", stderr=""),  # 2回目: gemini command
    ]

    main(run_once=True)

    mock_agent_client.return_value.request_task.assert_called_once()

    # Verify context.md was written correctly
    mock_file_open.assert_called_once_with("context.md", "w", encoding="utf-8")
    mock_file_open().write.assert_called_once_with(prompt_content.strip())

    # Verify subprocess was called correctly (2回)
    expected_calls = [
        call(["bash", ANY], check=True, capture_output=True, text=True),
        call(GEMINI_COMMAND, text=True, capture_output=True, check=True, shell=True),
    ]
    mock_subprocess_run.assert_has_calls(expected_calls)
    assert mock_subprocess_run.call_count == 2


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
@patch("agents_main.os.path.isfile", return_value=True)
@patch("agents_main.os.access", return_value=True)
def test_main_task_assigned_without_prompt(
    mock_os_access,
    mock_os_path_isfile,
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

    # 1回目の呼び出し (_run_update_context_script) のみをモック
    mock_subprocess_run.return_value = MagicMock(stdout="script output", stderr="")

    main(run_once=True)

    mock_agent_client.return_value.request_task.assert_called_once()

    # _run_update_context_script() の呼び出しのみが行われたことを検証
    mock_subprocess_run.assert_called_once_with(
        ["bash", ANY], check=True, capture_output=True, text=True
    )


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


@patch("builtins.open", new_callable=mock_open)
@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
@patch("agents_main.os.path.isfile", return_value=True)
@patch("agents_main.os.access", return_value=True)
def test_main_prompt_sanitization_removes_null_bytes(
    mock_os_access,
    mock_os_path_isfile,
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

    # 2回の呼び出しをモック
    mock_subprocess_run.side_effect = [
        MagicMock(
            stdout="script output", stderr=""
        ),  # 1回目: _run_update_context_script
        MagicMock(stdout="cli output", stderr=""),  # 2回目: gemini command
    ]

    main(run_once=True)

    # Verify context.md was written correctly
    mock_file_open.assert_called_once_with("context.md", "w", encoding="utf-8")
    mock_file_open().write.assert_called_once_with(expected_safe_prompt.strip())

    # Verify subprocess was called correctly (2回)
    expected_calls = [
        call(["bash", ANY], check=True, capture_output=True, text=True),
        call(GEMINI_COMMAND, text=True, capture_output=True, check=True, shell=True),
    ]
    mock_subprocess_run.assert_has_calls(expected_calls)
    assert mock_subprocess_run.call_count == 2


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
@patch("agents_main.logging.error")
@patch("agents_main.os.path.isfile", return_value=True)
@patch("agents_main.os.access", return_value=True)
def test_main_subprocess_called_process_error(
    mock_os_access,
    mock_os_path_isfile,
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

    # 1回目: _run_update_context_script は成功
    # 2回目: gemini command は失敗
    mock_subprocess_run.side_effect = [
        MagicMock(stdout="script output", stderr=""),
        subprocess.CalledProcessError(
            returncode=1, cmd=GEMINI_COMMAND, output="", stderr="cli error"
        ),
    ]

    main(run_once=True)

    # gemini cli の実行失敗時のエラーメッセージを検証
    mock_logging_error.assert_any_call(
        f"gemini cli の実行中にエラーが発生しました: Command '{GEMINI_COMMAND}' returned non-zero exit status 1."
    )
    mock_logging_error.assert_any_call("stdout: ")
    mock_logging_error.assert_any_call("stderr: cli error")


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
@patch("agents_main.os.path.isfile", return_value=True)
@patch("agents_main.os.access", return_value=True)
def test_main_run_once_true_exits_after_task(
    mock_os_access,
    mock_os_path_isfile,
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

    # 2回の呼び出しをモック
    mock_subprocess_run.side_effect = [
        MagicMock(
            stdout="script output", stderr=""
        ),  # 1回目: _run_update_context_script
        MagicMock(stdout="cli output", stderr=""),  # 2回目: gemini command
    ]

    main(run_once=True)
    mock_agent_client.return_value.request_task.assert_called_once()
    assert mock_subprocess_run.call_count == 2


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


@patch("agents_main.AgentClient")
@patch("agents_main.shutil.which")
@patch("agents_main.subprocess.run")
@patch("agents_main.os.path.isfile")
@patch("agents_main.os.access")
def test_main_context_script_fails_breaks_run_once(
    mock_os_access,
    mock_os_path_isfile,
    mock_subprocess_run,
    mock_shutil_which,
    mock_agent_client,
):
    # Arrange
    mock_shutil_which.return_value = "/usr/bin/gemini"
    # request_taskが呼ばれた回数を検証するために、side_effectは使わず、request_taskのモックを直接検証する
    mock_agent_client.return_value.request_task.return_value = {
        "issue_id": 1,
        "title": "Test Task",
        "prompt": "test prompt",
    }

    # スクリプトの存在はOKだが、実行に失敗するケースをシミュレート
    mock_os_path_isfile.return_value = True
    mock_os_access.return_value = True
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd="bash script", output="", stderr="script error"
    )

    # Act
    main(run_once=True)

    # Assert
    # 1回目の request_task は呼ばれる
    mock_agent_client.return_value.request_task.assert_called_once()
    # subprocess.run は呼ばれる
    mock_subprocess_run.assert_called_once()
    # 2回目の request_task は呼ばれない (breakしたため)
    assert mock_agent_client.return_value.request_task.call_count == 1
