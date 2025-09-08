import os

import pytest
from pydantic import ValidationError

from github_broker.infrastructure.config import Settings


# 環境変数を一時的に設定・解除するためのフィクスチャ
@pytest.fixture(autouse=True)
def clear_env_vars():
    original_env = os.environ.copy()
    keys_to_clear = [
        "GITHUB_TOKEN",
        "GEMINI_API_KEY",
        "GITHUB_WEBHOOK_SECRET",
        "BROKER_PORT",
        "GITHUB_REPOSITORY",
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_DB",
        "TESTING",
        "GITHUB_INDEXING_WAIT_SECONDS",
    ]
    for key in keys_to_clear:
        if key in os.environ:
            del os.environ[key]
    yield
    os.environ.clear()
    os.environ.update(original_env)


def test_settings_loads_from_env_vars():
    os.environ["GITHUB_TOKEN"] = "test_github_token"
    os.environ["GEMINI_API_KEY"] = "test_gemini_api_key"
    os.environ["GITHUB_WEBHOOK_SECRET"] = "test_webhook_secret"
    os.environ["GITHUB_REPOSITORY"] = "test_owner/test_repo"
    os.environ["BROKER_PORT"] = "9000"
    os.environ["REDIS_HOST"] = "test_redis_host"
    os.environ["REDIS_PORT"] = "6380"
    os.environ["REDIS_DB"] = "1"
    os.environ["TESTING"] = "True"

    settings = Settings()

    assert settings.GITHUB_TOKEN == "test_github_token"
    assert settings.GEMINI_API_KEY == "test_gemini_api_key"
    assert settings.GITHUB_WEBHOOK_SECRET == "test_webhook_secret"
    assert settings.GITHUB_REPOSITORY == "test_owner/test_repo"
    assert settings.BROKER_PORT == 9000
    assert settings.REDIS_HOST == "test_redis_host"
    assert settings.REDIS_PORT == 6380
    assert settings.REDIS_DB == 1
    assert settings.TESTING is True


def test_settings_uses_default_values():
    # 必須の環境変数を設定
    os.environ["GITHUB_TOKEN"] = "dummy_github_token"
    os.environ["GEMINI_API_KEY"] = "dummy_gemini_api_key"
    os.environ["GITHUB_WEBHOOK_SECRET"] = "dummy_webhook_secret"
    os.environ["GITHUB_REPOSITORY"] = "dummy_owner/dummy_repo"

    settings = Settings()

    assert settings.BROKER_PORT == 8000
    assert settings.REDIS_HOST == "localhost"
    assert settings.REDIS_PORT == 6379
    assert settings.REDIS_DB == 0
    assert settings.TESTING is False


def test_settings_raises_error_if_required_env_vars_missing():
    # GITHUB_TOKENが欠けている場合
    with pytest.raises(ValidationError):
        Settings()

    os.environ["GITHUB_TOKEN"] = "dummy_github_token"
    # GEMINI_API_KEYが欠けている場合
    with pytest.raises(ValidationError):
        Settings()

    os.environ["GEMINI_API_KEY"] = "dummy_gemini_api_key"
    # GITHUB_WEBHOOK_SECRETが欠けている場合
    with pytest.raises(ValidationError):
        Settings()

    os.environ["GITHUB_WEBHOOK_SECRET"] = "dummy_webhook_secret"
    # GITHUB_REPOSITORYが欠けている場合
    with pytest.raises(ValidationError):
        Settings()
