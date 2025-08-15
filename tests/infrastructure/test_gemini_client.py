import pytest
import textwrap
from unittest.mock import patch, MagicMock

from github_broker.infrastructure.gemini_client import GeminiClient


@patch('os.getenv')
def test_gemini_client_init_success(mock_getenv):
    """
    Test that GeminiClient initializes successfully when GEMINI_API_KEY is set.
    """
    mock_getenv.return_value = "fake_gemini_api_key"
    client = GeminiClient()
    assert client._api_key == "fake_gemini_api_key"
    mock_getenv.assert_called_once_with("GEMINI_API_KEY")


@patch('os.getenv')
def test_gemini_client_init_no_api_key(mock_getenv):
    """
    Test that GeminiClient raises ValueError if GEMINI_API_KEY is not set.
    """
    mock_getenv.return_value = None
    with pytest.raises(ValueError, match="Gemini API key not found in GEMINI_API_KEY environment variable."):
        GeminiClient()
    mock_getenv.assert_called_once_with("GEMINI_API_KEY")

@patch('os.getenv')
def test_select_best_issue_id_no_issues(mock_getenv):
    """
    Test select_best_issue_id when no issues are provided.
    """
    mock_getenv.return_value = "fake_gemini_api_key"
    client = GeminiClient()

    issues = []
    capabilities = ["python"]

    selected_id = client.select_best_issue_id(issues, capabilities)

    assert selected_id is None

@patch('os.getenv')
@patch('github_broker.infrastructure.gemini_client.genai.GenerativeModel')
def test_select_best_issue_id_with_gemini_api_call(mock_generative_model, mock_getenv):
    """
    Test that select_best_issue_id correctly calls the Gemini API,
    generates a prompt, and parses the response.
    """
    # Arrange
    mock_getenv.return_value = "fake_gemini_api_key"

    # Mock the response from the Gemini API
    mock_gemini_response = MagicMock()
    # The response text should be a JSON string.
    mock_gemini_response.text = '{"issue_id": 101}'
    
    # The model's generate_content method returns the mock response
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_gemini_response
    mock_generative_model.return_value = mock_model_instance

    client = GeminiClient()

    issues = [
        {"id": 101, "title": "Refactor database module", "body": "The DB module is too complex.", "labels": ["refactoring", "python"]},
        {"id": 102, "title": "Fix login bug", "body": "User cannot log in.", "labels": ["bug", "frontend"]},
    ]
    capabilities = ["python", "refactoring", "backend"]

    # Act
    selected_id = client.select_best_issue_id(issues, capabilities)

    # Assert
    # Verify that the model was called
    mock_model_instance.generate_content.assert_called_once()
    
    # Get the actual prompt sent to the model
    actual_prompt = mock_model_instance.generate_content.call_args[0][0]

    # Verify the prompt contains key information
    assert "Refactor database module" in actual_prompt
    assert "python" in actual_prompt
    assert "refactoring" in actual_prompt
    assert "backend" in actual_prompt
    # Check for a key phrase from the dedented prompt
    assert "You are an expert software development project manager." in actual_prompt
    assert '{"issue_id": <id>}' in actual_prompt

    # Verify the result is correctly parsed
    assert selected_id == 101
