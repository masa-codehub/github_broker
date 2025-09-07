from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor

PROMPT_FILE_CONTENT = """
build_prompt: |
  Title: {title}
  Branch: {branch_name}
  Body: {body}
review_prompt: |
  Original: {original_prompt}
  Output: {execution_output}
"""


@pytest.fixture
def mock_prompts():
    """ロードされたプロンプトの辞書をモックします"""
    return yaml.safe_load(PROMPT_FILE_CONTENT)


@pytest.fixture
def executor(mock_prompts):
    """プロンプトがモックされた、テスト用のGeminiExecutorインスタンスを提供します"""
    with (
        patch("builtins.open", mock_open(read_data=PROMPT_FILE_CONTENT)),
        patch("yaml.safe_load", return_value=mock_prompts),
        patch("os.makedirs"),
    ):
        # __init__ 内でファイルIOとyamlパースがモックされる
        return GeminiExecutor(log_dir="/app/logs")


@pytest.mark.unit
def test_init_loads_prompts_from_file(mock_prompts):
    """__init__がプロンプトファイルを正しく読み込むことをテストします"""
    # Arrange
    prompt_file_path = "dummy/path/prompts.yml"
    with (
        patch("builtins.open", mock_open(read_data=PROMPT_FILE_CONTENT)) as mock_file,
        patch("yaml.safe_load", return_value=mock_prompts) as mock_safe_load,
    ):
        # Act
        executor_instance = GeminiExecutor(prompt_file=prompt_file_path)

        # Assert
        mock_file.assert_called_once_with(prompt_file_path, encoding="utf-8")
        mock_safe_load.assert_called_once()
        assert executor_instance.build_prompt_template == mock_prompts["build_prompt"]
        assert executor_instance.review_prompt_template == mock_prompts["review_prompt"]


@pytest.mark.unit
def test_init_handles_prompt_file_error():
    """__init__がプロンプトファイルのFileNotFoundErrorを処理することをテストします。"""
    # Arrange
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError

        # Act
        executor_instance = GeminiExecutor(prompt_file="nonexistent.yml")

        # Assert
        assert executor_instance.build_prompt_template == ""
        assert executor_instance.review_prompt_template == ""


@pytest.mark.unit
def test_build_prompt(executor):
    """_build_promptがテンプレートに基づいてプロンプトを正しく構築することをテストします"""
    # Act
    prompt = executor._build_prompt("Test Title", "Test Body", "feature/test")

    # Assert
    assert prompt == "Title: Test Title\nBranch: feature/test\nBody: Test Body\n"


@pytest.mark.unit
def test_build_review_prompt(executor):
    """_build_review_promptがテンプレートに基づいてプロンプトを正しく構築することをテストします"""
    # Act
    review_prompt = executor._build_review_prompt("Original", "Output")

    # Assert
    assert review_prompt == "Original: Original\nOutput: Output\n"


@pytest.mark.unit
@patch(
    "github_broker.infrastructure.executors.gemini_executor.GeminiExecutor._run_sub_process"
)
def test_execute_success(mock_run_sub_process, executor):
    """タスクの正常な実行（初回＋レビュー）をテストします"""
    # Arrange
    mock_run_sub_process.return_value = True
    task = {
        "title": "Test Title",
        "body": "Test Body",
        "branch_name": "feature/test",
        "agent_id": "test-agent",
    }
    # openをモックして、ログファイルの読み書きをシミュレート
    with patch("builtins.open", mock_open(read_data="initial output")):
        # Act
        executor.execute(task)

    # Assert
    assert mock_run_sub_process.call_count == 2


@pytest.mark.unit
@patch(
    "github_broker.infrastructure.executors.gemini_executor.GeminiExecutor._run_sub_process"
)
def test_execute_first_run_fails(mock_run_sub_process, executor):
    """初回実行が失敗した場合、レビューステップがスキップされることをテストします"""
    # Arrange
    mock_run_sub_process.return_value = False  # 実行失敗をシミュレート
    task = {"title": "t", "body": "b", "branch_name": "b", "agent_id": "test-agent"}

    # Act
    executor.execute(task)

    # Assert
    mock_run_sub_process.assert_called_once()


@pytest.mark.unit
@patch(
    "github_broker.infrastructure.executors.gemini_executor.GeminiExecutor._run_sub_process"
)
def test_execute_handles_log_read_error(mock_run_sub_process, executor):
    """ログファイルの読み込み失敗時にレビューがスキップされることをテストします"""
    # Arrange
    mock_run_sub_process.return_value = True
    task = {"title": "t", "body": "b", "branch_name": "b", "agent_id": "test-agent"}

    # openをモックして、読み込み時にエラーを発生させる
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = OSError("Failed to read")
        # Act
        executor.execute(task)

    # Assert
    # 初回実行は呼ばれるが、レビューのための2回目の実行はスキップされる
    mock_run_sub_process.assert_called_once()


@pytest.mark.unit
@patch("subprocess.Popen")
def test_run_sub_process_handles_file_not_found(mock_popen, executor):
    """_run_sub_processがFileNotFoundErrorを処理することをテストします"""
    # Arrange
    mock_popen.side_effect = FileNotFoundError("Command not found")

    # Act
    result = executor._run_sub_process(["gemini"], "/tmp/log.txt")

    # Assert
    assert result is False


@pytest.mark.unit
@patch("subprocess.Popen")
def test_run_sub_process_handles_generic_exception(mock_popen, executor):
    """_run_sub_processが一般的な例外を処理することをテストします"""
    # Arrange
    mock_popen.side_effect = Exception("Unexpected error")

    # Act
    result = executor._run_sub_process(["some", "command"], "/tmp/log.txt")

    # Assert
    assert result is False


@pytest.mark.unit
def test_get_log_filepath_no_log_dir():
    """_get_log_filepathがlog_dirなしでNoneを返すことをテストします。"""
    # Arrange
    executor = GeminiExecutor(log_dir=None)
    # Act
    filepath = executor._get_log_filepath("test-agent")
    # Assert
    assert filepath is None


@pytest.mark.unit
def test_get_log_filepath_no_agent_id(executor):
    """_get_log_filepathがagent_idなしでNoneを返すことをテストします。"""
    # Act
    with patch("logging.warning") as mock_log_warning:
        filepath = executor._get_log_filepath(None)
    # Assert
    assert filepath is None
    mock_log_warning.assert_called_once()


@pytest.mark.unit
@patch("subprocess.Popen")
def test_run_sub_process_captures_output(mock_popen, executor):
    """_run_sub_processがサブプロセスの出力を正しくキャプチャすることをテストします。"""
    # Arrange
    mock_process = MagicMock()
    mock_process.stdout = ["line 1\n", "line 2\n"]
    mock_process.returncode = 0
    mock_popen.return_value.__enter__.return_value = mock_process

    mock_log_file = mock_open()

    # Act
    with patch("builtins.open", mock_log_file):
        result = executor._run_sub_process(["dummy_command"], "/dummy/log.txt")

    # Assert
    assert result is True
    handle = mock_log_file()
    assert handle.write.call_count == 2
    assert handle.write.call_args_list[0].args == ("line 1\n",)
    assert handle.write.call_args_list[1].args == ("line 2\n",)
