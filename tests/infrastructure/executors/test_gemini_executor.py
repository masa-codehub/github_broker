from unittest.mock import mock_open, patch

import pytest
import yaml

from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor

PROMPT_FILE_CONTENT = """
prompt_template: |
  Issue ID: {issue_id}
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
        assert (
            executor_instance.build_prompt_template == mock_prompts["prompt_template"]
        )


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


@pytest.mark.unit
def test_build_prompt(executor):
    """_build_promptがテンプレートに基づいてプロンプトを正しく構築することをテストします"""
    # Act
    prompt = executor.build_prompt(123, "Test Title", "Test Body", "feature/test")

    # Assert
    assert (
        prompt
        == "Issue ID: 123\nTitle: Test Title\nBranch: feature/test\nBody: Test Body\n"
    )
