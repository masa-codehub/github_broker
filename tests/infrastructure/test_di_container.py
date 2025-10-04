import os
from unittest.mock import patch

import pytest

import github_broker.infrastructure.di_container as di_container_module
from github_broker.application.task_service import TaskService


@pytest.fixture(autouse=True)
def reset_container():
    """Ensures each test gets a fresh DI container."""
    di_container_module._container = None


@pytest.mark.integration
def test_di_container_resolves_task_service_instance():
    """
    DIコンテナが設定と依存関係を解決し、TaskServiceのインスタンスを
    正常に作成できることを検証する統合テスト。
    """

    test_env = {
        "GITHUB_REPOSITORY": "test/repo",
        "GITHUB_TOKEN": "fake-token",
        "GEMINI_API_KEY": "fake-gemini-key",
        "GITHUB_INDEXING_WAIT_SECONDS": "10",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_DB": "0",
    }
    with patch.dict(os.environ, test_env):
        # Act
        # 環境変数が設定されたコンテキスト内でコンテナを生成・解決
        container = di_container_module.get_container()
        service = container.resolve(TaskService)

        # Assert
        assert isinstance(service, TaskService)
        # 内部のクライアントも正しく設定されているかを確認
        assert service.repo_name == "test/repo"
        assert service.github_indexing_wait_seconds == 10
