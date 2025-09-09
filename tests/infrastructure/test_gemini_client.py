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
def test_select_best_issue_id_no_issues():
    """
    Issueが提供されない場合にselect_best_issue_idがNoneを返すことをテストします。
    """
    client = GeminiClient("fake_gemini_api_key")

    issues = []
    capabilities = ["python"]

    selected_id = client.select_best_issue_id(issues, capabilities)

    assert selected_id is None


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

    issues = [
        {
            "id": 101,
            "title": "データベースモジュールのリファクタリング",
            "body": "DBモジュールは複雑すぎます。",
            "labels": ["refactoring", "python"],
        },
        {
            "id": 102,
            "title": "ログインバグの修正",
            "body": "ユーザーがログインできません。",
            "labels": ["bug", "frontend"],
        },
    ]
    capabilities = ["python", "refactoring", "backend"]

    # Act
    selected_id = client.select_best_issue_id(issues, capabilities)

    # Assert
    # モデルが呼び出されたことを確認
    mock_model_instance.generate_content.assert_called_once()

    # モデルに送信された実際のプロンプトを取得
    actual_prompt = mock_model_instance.generate_content.call_args[0][0]

    # プロンプトに重要な情報が含まれていることを確認
    assert "データベースモジュールのリファクタリング" in actual_prompt
    assert "python" in actual_prompt
    assert "refactoring" in actual_prompt
    assert "backend" in actual_prompt
    # プロンプトからキーフレーズを確認
    assert (
        "あなたは熟練したソフトウェア開発プロジェクトマネージャーです。"
        in actual_prompt
    )

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
    issues = [{"id": 1, "title": "Test"}]
    capabilities = ["test"]

    # Act
    selected_id = client.select_best_issue_id(issues, capabilities)

    # Assert
    assert selected_id is None


@pytest.mark.unit
@patch("github_broker.infrastructure.gemini_client.genai.GenerativeModel")
def test_select_best_issue_id_fallback_on_api_error(mock_generative_model):
    """
    API呼び出しが失敗した場合にselect_best_issue_idが最初のIssueにフォールバックすることをテストします。
    """
    # Arrange
    # API呼び出しが例外を発生させるようにモック
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.side_effect = Exception("API Key Invalid")
    mock_generative_model.return_value = mock_model_instance

    client = GeminiClient("fake_gemini_api_key")

    issues = [
        {"id": 201, "title": "最初のIssue"},
        {"id": 202, "title": "2番目のIssue"},
    ]
    capabilities = ["*"]

    # Act
    selected_id = client.select_best_issue_id(issues, capabilities)

    # Assert
    # フォールバック機能が最初のIssueのIDを返したことを確認
    assert selected_id == 201
