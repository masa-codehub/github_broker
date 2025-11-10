from unittest.mock import patch

import punq

from github_broker.application.task_service import TaskService
from github_broker.domain.agent_config import AgentConfigList
from github_broker.infrastructure.agent.loader import AgentConfigLoader
from github_broker.infrastructure.config import Settings
from github_broker.infrastructure.di_container import create_container
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient


@patch("github_broker.infrastructure.agent.loader.AgentConfigLoader.load_from_file")
def test_create_container(mock_load_from_file, monkeypatch):
    """
    Tests the create_container function by mocking environment variables
    and verifying that all dependencies are correctly instantiated.
    """
    # Arrange
    # Use monkeypatch to set environment variables for the Settings object
    monkeypatch.setenv("GITHUB_APP_ID", "test_id")
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY", "test_key")
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN", "test_token")
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test_secret")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key")
    monkeypatch.setenv("GITHUB_AGENT_REPOSITORY", "test_owner/test_repo")

    mock_agent_config_list = AgentConfigList(agents=[])
    mock_load_from_file.return_value = mock_agent_config_list

    # Act
    # We call create_container without arguments, so it uses get_settings()
    # which will now pick up the mocked environment variables.
    container = create_container()

    # Assert
    assert isinstance(container, punq.Container)
    resolved_settings = container.resolve(Settings)
    assert resolved_settings.github_app_id == "test_id"
    assert resolved_settings.github_agent_repository == "test_owner/test_repo"

    assert isinstance(container.resolve(GitHubClient), GitHubClient)
    assert isinstance(container.resolve(RedisClient), RedisClient)
    assert isinstance(container.resolve(AgentConfigLoader), AgentConfigLoader)
    assert container.resolve(AgentConfigList) == mock_agent_config_list
    assert isinstance(container.resolve(TaskService), TaskService)

    # Verify that load_from_file was called
    mock_load_from_file.assert_called_once_with("agents.toml")
