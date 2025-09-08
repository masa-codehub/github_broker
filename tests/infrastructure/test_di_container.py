import os
from unittest.mock import patch

import pytest

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.di_container import create_container


@pytest.mark.integration
def test_di_container_resolves_task_service_instance():
    """
    DIコンテナが設定と依存関係を解決し、TaskServiceのインスタンスを
    正常に作成できることを検証する統合テスト。
    """
    # Arrange: 実際のインスタンス化に必要な環境変数をすべて設定
    test_env = {
        "GITHUB_REPOSITORY": "test/repo",
        "GITHUB_TOKEN": "fake-token",
        "GEMINI_API_KEY": "fake-gemini-key",
        "GITHUB_INDEXING_WAIT_SECONDS": "10",
        "GITHUB_WEBHOOK_SECRET": "fake-secret-for-testing",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_DB": "0",
    }
    with patch.dict(os.environ, test_env):
        # Act
        # 環境変数が設定されたコンテキスト内でコンテナを生成・解決
        container = create_container()
        service = container.resolve(TaskService)

        # Assert
        assert isinstance(service, TaskService)
        # 内部のクライアントも正しく設定されているかを確認
        assert service.repo_name == "test/repo"
        assert service.github_indexing_wait_seconds == 10
