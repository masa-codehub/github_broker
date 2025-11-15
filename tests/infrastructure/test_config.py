from unittest.mock import patch

from github_broker.infrastructure.config import get_settings


def test_settings_load_from_env():
    with patch.dict(
        "os.environ",
        {
            "GITHUB_APP_ID": "12345",
            "GITHUB_APP_PRIVATE_KEY": "test_key",
            "GITHUB_PERSONAL_ACCESS_TOKEN": "test_token",
            "GITHUB_WEBHOOK_SECRET": "test_secret",
            "REDIS_URL": "redis://test:6379",
            "GOOGLE_API_KEY": "test_google_key",
        },
    ):
        settings = get_settings()
        assert settings.github_app_id == "12345"
        assert settings.github_app_private_key == "test_key"
        assert settings.github_personal_access_token == "test_token"
        assert settings.github_webhook_secret == "test_secret"
        assert settings.redis_url == "redis://test:6379"
        assert settings.google_api_key == "test_google_key"


def test_settings_defaults():
    with patch.dict(
        "os.environ",
        {
            "GITHUB_APP_ID": "12345",
            "GITHUB_APP_PRIVATE_KEY": "test_key",
            "GITHUB_PERSONAL_ACCESS_TOKEN": "test_token",
            "GITHUB_WEBHOOK_SECRET": "test_secret",
            "GOOGLE_API_KEY": "test_google_key",
        },
    ):
        settings = get_settings()
        assert settings.redis_url == "redis://localhost:6379"
        assert settings.github_agent_repository == "gemini-code-assist/gemini-code-assist"
