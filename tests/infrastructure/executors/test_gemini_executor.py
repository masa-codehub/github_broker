from unittest.mock import MagicMock, patch

import pytest

from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor


@pytest.fixture
def executor():
    """ログディレクトリが設定された、テスト用のGeminiExecutorインスタンスを提供します。"""
    with patch("os.makedirs"):
        return GeminiExecutor(log_dir="/app/logs")


@patch("subprocess.Popen")
def test_execute_success(mock_popen, executor):
    """
    タスクの正常な実行をテストします。
    """
    # Arrange
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = ["line 1", "line 2"]
    mock_popen.return_value.__enter__.return_value = mock_proc

    task = {
        "title": "Test Title",
        "body": "Test Body",
        "branch_name": "feature/test",
        "agent_id": "test-agent",
    }

    # Act
    with (
        patch("builtins.open"),
        patch(
            "github_broker.infrastructure.executors.gemini_executor.GeminiExecutor._run_sub_process"
        ) as mock_run,
    ):
        mock_run.return_value = True
        executor.execute(task)

    # Assert
    assert mock_run.call_count == 2  # 初回実行とレビューフェーズ


@patch("subprocess.Popen")
def test_execute_command_fails(mock_popen, executor):
    """
    gemini cliコマンドが0以外の終了コードを返した場合をテストします。
    """
    # Arrange
    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.stdout = ["error occurred"]
    mock_popen.return_value.__enter__.return_value = mock_proc
    task = {"title": "t", "body": "b", "branch_name": "b", "agent_id": "test-agent"}

    # Act
    with patch(
        "github_broker.infrastructure.executors.gemini_executor.GeminiExecutor._run_sub_process"
    ) as mock_run_sub_process:
        mock_run_sub_process.return_value = False
        executor.execute(task)

    # Assert
    mock_run_sub_process.assert_called_once()


@patch("subprocess.Popen", side_effect=FileNotFoundError("Command not found"))
def test_execute_file_not_found(mock_popen, executor):
    """
    gemini cliコマンドが見つからない場合をテストします。
    """
    # Arrange
    task = {"title": "t", "body": "b", "branch_name": "b", "agent_id": "test-agent"}

    # Act
    with patch(
        "github_broker.infrastructure.executors.gemini_executor.GeminiExecutor._run_sub_process"
    ) as mock_run_sub_process:
        mock_run_sub_process.return_value = False
        executor.execute(task)

    # Assert
    mock_run_sub_process.assert_called_once()


def test_build_review_prompt(executor):
    """_build_review_promptメソッドをテストします。"""
    original_prompt = "Original instruction"
    execution_output = "Initial output"
    review_prompt = executor._build_review_prompt(original_prompt, execution_output)
    assert "あなたはシニア品質保証エンジニアです。" in review_prompt
    assert original_prompt in review_prompt
    assert execution_output in review_prompt


def test_get_log_filepath_success():
    """_get_log_filepathがlog_dir設定時に正しいパスを返すことをテストします。"""
    with patch("os.makedirs"):
        executor = GeminiExecutor(log_dir="/tmp/logs")
        filepath = executor._get_log_filepath("test-agent")
        assert filepath.startswith("/tmp/logs/test-agent_")
        assert filepath.endswith(".md")


def test_get_log_filepath_no_log_dir():
    """_get_log_filepathがlog_dir未設定時にNoneを返すことをテストします。"""
    executor = GeminiExecutor(log_dir=None)
    filepath = executor._get_log_filepath("test-agent")
    assert filepath is None


def test_get_log_filepath_no_agent_id():
    """_get_log_filepathがagent_id未提供時にNoneを返すことをテストします。"""
    with patch("os.makedirs"):
        executor = GeminiExecutor(log_dir="/app/logs")
        filepath = executor._get_log_filepath(None)
        assert filepath is None


@patch(
    "github_broker.infrastructure.executors.gemini_executor.GeminiExecutor._run_sub_process"
)
def test_execute_handles_log_read_error(mock_run_sub_process, executor):
    """ログファイルの読み込み失敗時にレビューがスキップされることをテストします。"""
    mock_run_sub_process.return_value = True
    task = {"title": "t", "body": "b", "branch_name": "b", "agent_id": "test-agent"}

    with patch("builtins.open", side_effect=OSError("Failed to read")):
        executor.execute(task)

    # Assert that only the first call to _run_sub_process happened
    mock_run_sub_process.assert_called_once()


@patch("subprocess.Popen", side_effect=Exception("Unexpected error"))
def test_run_sub_process_handles_generic_exception(mock_popen, executor):
    """_run_sub_processが一般的な例外を処理することをテストします。"""
    result = executor._run_sub_process(["some", "command"], "/tmp/log.txt")
    assert result is False
