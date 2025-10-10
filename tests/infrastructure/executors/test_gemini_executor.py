import os
from unittest.mock import mock_open, patch

import pytest
import yaml

import github_broker
from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor

# Load the actual prompt content from the production file
PROMPT_FILE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(
            github_broker.infrastructure.executors.gemini_executor.__file__
        ),
        "..",
        "prompts",
        "gemini_executor.yml",
    )
)
with open(PROMPT_FILE_PATH, encoding="utf-8") as f:
    PROMPT_FILE_CONTENT = f.read()


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
    prompt_file_path = "prompts/gemini_executor.yml"
    with (
        patch("builtins.open", mock_open(read_data=PROMPT_FILE_CONTENT)) as mock_file,
        patch("yaml.safe_load", return_value=mock_prompts) as mock_safe_load,
    ):
        executor_instance = GeminiExecutor(prompt_file=prompt_file_path)

        # GeminiExecutorが内部でパスを解決するのと同じロジックを適用
        expected_path = os.path.abspath(
            os.path.join(
                os.path.dirname(
                    github_broker.infrastructure.executors.gemini_executor.__file__
                ),
                "..",
                "prompts",
                os.path.basename(prompt_file_path),
            )
        )
        mock_file.assert_called_once_with(expected_path, encoding="utf-8")
        mock_safe_load.assert_called_once()
        assert (
            executor_instance.build_prompt_template
            == mock_prompts["prompt_template"].strip()
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
def test_build_prompt_with_pr_and_comments(executor, mock_prompts):
    """build_promptがPRのURLとレビューコメントを正しく生成することをテストします"""
    # Arrange
    pr_url = "https://github.com/example/repo/pull/456"
    review_comments = ["Comment 1", "Comment 2", "Comment 3"]
    html_url = "https://github.com/example/repo/issues/123"
    branch_name = "feature/test"

    # Act
    prompt = executor.build_prompt(
        html_url=html_url,
        branch_name=branch_name,
        pr_url=pr_url,
        review_comments=review_comments,
    )

    # Assert
    expected_prompt = (
        mock_prompts["prompt_template"]
        .strip()
        .format(
            html_url=html_url,
            branch_name=branch_name,
            pr_url=pr_url,
            review_comments="\n".join(review_comments),
        )
    )
    assert prompt == expected_prompt


@pytest.mark.unit
def test_build_prompt_with_no_pr_or_comments(executor, mock_prompts):
    """build_promptがPRのURLとレビューコメントがない場合に正しく生成することをテストします"""
    # Arrange
    html_url = "https://github.com/example/repo/issues/123"
    branch_name = "feature/test"

    # Act
    prompt = executor.build_prompt(
        html_url=html_url,
        branch_name=branch_name,
    )

    # Assert
    expected_prompt = (
        mock_prompts["prompt_template"]
        .strip()
        .format(
            html_url=html_url,
            branch_name=branch_name,
            pr_url="N/A",
            review_comments="N/A",
        )
    )
    assert prompt == expected_prompt


@pytest.mark.unit
def test_init_handles_empty_yaml_file():
    """__init__が空のYAMLファイルを処理することをテストします。"""
    # Arrange
    with (
        patch("builtins.open", mock_open(read_data="")),
        patch("yaml.safe_load", return_value=None),
    ):
        # Act
        executor_instance = GeminiExecutor(prompt_file="empty.yml")

        # Assert
        assert executor_instance.build_prompt_template == ""
        assert executor_instance.review_fix_prompt_template == ""


@pytest.mark.unit
def test_init_handles_missing_prompt_template_key(mock_prompts):
    """__init__が'prompt_template'キーの欠損を処理することをテストします。"""
    # Arrange
    del mock_prompts["prompt_template"]
    with (
        patch("builtins.open", mock_open(read_data=PROMPT_FILE_CONTENT)),
        patch("yaml.safe_load", return_value=mock_prompts),
    ):
        # Act
        executor_instance = GeminiExecutor(prompt_file="prompts.yml")

        # Assert
        assert executor_instance.build_prompt_template == ""
        assert (
            executor_instance.review_fix_prompt_template
            == mock_prompts["review_fix_prompt_template"].strip()
        )


@pytest.mark.unit
def test_init_handles_missing_review_fix_prompt_template_key(mock_prompts):
    """__init__が'review_fix_prompt_template'キーの欠損を処理することをテストします。"""
    # Arrange
    del mock_prompts["review_fix_prompt_template"]
    with (
        patch("builtins.open", mock_open(read_data=PROMPT_FILE_CONTENT)),
        patch("yaml.safe_load", return_value=mock_prompts),
    ):
        # Act
        executor_instance = GeminiExecutor(prompt_file="prompts.yml")

        # Assert
        assert (
            executor_instance.build_prompt_template
            == mock_prompts["prompt_template"].strip()
        )
        assert executor_instance.review_fix_prompt_template == ""
