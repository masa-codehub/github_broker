from unittest.mock import MagicMock, patch

import pytest

from github_broker.infrastructure.gemini_client import GeminiClient


@pytest.mark.unit
def test_gemini_client_init_success():
    """
    GEMINI_API_KEYが設定されている場合にGeminiClientが正常に初期化されることをテストします。
    """
    client = GeminiClient("fake_gemini_api_key")
    assert client._api_key == "fake_gemini_api_key"


@pytest.mark.unit
@patch("github_broker.infrastructure.gemini_client.genai.GenerativeModel")
def test_select_best_issue_id_no_issues(mock_generative_model):
    """
    Issueが提供されない場合にselect_best_issue_idがNoneを返すことをテストします。
    """
    mock_gemini_response = MagicMock()
    mock_gemini_response.text = '{"issue_id": null}'
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_gemini_response
    mock_generative_model.return_value = mock_model_instance

    client = GeminiClient("fake_gemini_api_key")
    prompt = "No issues available."

    selected_id = client.select_best_issue_id(prompt)

    assert selected_id is None
    mock_model_instance.generate_content.assert_called_once_with(prompt)


@pytest.mark.unit
@patch("github_broker.infrastructure.gemini_client.genai.GenerativeModel")
def test_select_best_issue_id_with_gemini_api_call(mock_generative_model):
    """
    select_best_issue_idがGemini APIを正しく呼び出し、プロンプトを生成し、レスポンスを解析することをテストします。
    """
    # Arrange
    # Gemini APIからのレスポンスをモック
    mock_gemini_response = MagicMock()
    # レスポンスのテキストはJSON文字列であるべき
    mock_gemini_response.text = '{"issue_id": 101}'

    # モデルのgenerate_contentメソッドがモックレスポンスを返すように設定
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_gemini_response
    mock_generative_model.return_value = mock_model_instance

    client = GeminiClient("fake_gemini_api_key")

    # 事前に構築されたプロンプトを準備
    pre_built_prompt = (
        "あなたは熟練したソフトウェア開発プロジェクトマネージャーです。\n"
        "以下のIssue情報に基づいて、最適なIssue IDをJSON形式で出力してください。\n"
        "Issue IDのみを出力し、他のテキストは含めないでください。\n"
        "\n"
        "---\n"
        "Issue ID: 101\n"
        "タイトル: データベースモジュールのリファクタリング\n"
        "本文: DBモジュールは複雑すぎます。\n"
        "ラベル: refactoring, python\n"
        "---\n"
        "Issue ID: 102\n"
        "タイトル: ログインバグの修正\n"
        "本文: ユーザーがログインできません。\n"
        "ラベル: bug, frontend\n"
        "---\n"
        "\n"
        "エージェントの機能: python, refactoring, backend\n"
        "\n"
        "最適なIssue IDをJSON形式で出力してください。\n"
        '例: {"issue_id": 123}'
    )

    # Act
    selected_id = client.select_best_issue_id(pre_built_prompt)

    # Assert
    # モデルが呼び出されたことを確認
    mock_model_instance.generate_content.assert_called_once_with(pre_built_prompt)

    # 結果が正しく解析されたことを確認
    assert selected_id == 101


@pytest.mark.unit
@patch("github_broker.infrastructure.gemini_client.genai.GenerativeModel")
def test_select_best_issue_id_handles_null_id(mock_generative_model):
    """Geminiがnullのissue_idを返した場合にNoneを返すことをテストします。"""
    # Arrange
    mock_gemini_response = MagicMock()
    mock_gemini_response.text = '{"issue_id": null}'
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_gemini_response
    mock_generative_model.return_value = mock_model_instance

    client = GeminiClient("fake_gemini_api_key")
    prompt = "Issue IDを返さないプロンプト"

    # Act
    selected_id = client.select_best_issue_id(prompt)

    # Assert
    assert selected_id is None
    mock_model_instance.generate_content.assert_called_once_with(prompt)
