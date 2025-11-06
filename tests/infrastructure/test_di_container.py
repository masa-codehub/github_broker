import os
from unittest.mock import patch

import pytest

import github_broker.infrastructure.di_container as di_container_module
from github_broker.application.task_service import TaskService
from github_broker.infrastructure.agent.models import AgentDefinition


@pytest.fixture(autouse=True)
def reset_container():
    """Ensures each test gets a fresh DI container."""
    di_container_module._container = None


@pytest.mark.integration
@patch(
    "github_broker.infrastructure.agent.loader.AgentConfigLoader.load_config",
    return_value=[AgentDefinition(role="TEST_AGENT", description="A test agent")],
)
def test_di_container_resolves_task_service_instance(mock_load_config):
    """
    DIコンテナが設定と依存関係を解決し、TaskServiceのインスタンスを
    正常に作成できることを検証する統合テスト。
    AgentConfigLoader.load_configをモック化し、ファイルシステムの存在に依存しないようにする。
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
        # モックが呼ばれ、設定が反映されていることを確認
        mock_load_config.assert_called_once()
        assert len(service.agent_configs) == 1
        assert service.agent_configs[0].role == "TEST_AGENT"

