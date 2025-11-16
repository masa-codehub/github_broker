from unittest.mock import MagicMock

import pytest

from github_broker.application.task_service import TaskService
from github_broker.domain.agent_config import AgentConfigList, AgentDefinition
from github_broker.domain.task import Task


@pytest.fixture
def mock_github_client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_redis_client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_agent_configs() -> AgentConfigList:
    return AgentConfigList(
        agents=[
            AgentDefinition(role="test_role", persona="test_persona"),
            AgentDefinition(role="another_role", persona="another_persona"),
        ]
    )


@pytest.fixture
def task_service(
    mock_github_client: MagicMock,
    mock_redis_client: MagicMock,
    mock_agent_configs: AgentConfigList,
) -> TaskService:
    return TaskService(
        github_client=mock_github_client,
        redis_client=mock_redis_client,
        agent_configs=mock_agent_configs,
    )


def test_task_service_initialization(
    task_service: TaskService, mock_agent_configs: AgentConfigList
):
    """Tests if the TaskService correctly initializes the agent_roles."""
    # Assert
    expected_roles = {
        agent.role: agent.persona for agent in mock_agent_configs.get_all()
    }
    assert task_service.agent_roles == expected_roles


def test_create_task(task_service: TaskService):
    """Tests if _create_task correctly creates a Task object from an issue dict."""
    # Arrange
    issue = {
        "number": 123,
        "title": "Test Issue",
        "body": "This is a test body.",
        "html_url": "http://example.com/issue/123",
        "labels": [{"name": "bug"}, {"name": "feature"}],
    }

    # Act
    task = task_service._create_task(issue)

    # Assert
    assert isinstance(task, Task)
    assert task.issue_id == 123
    assert task.title == "Test Issue"
    assert task.body == "This is a test body."
    assert task.html_url == "http://example.com/issue/123"
    assert task.labels == ["bug", "feature"]


def test_request_task(task_service: TaskService):
    """
    Tests if request_task runs without error.
    NOTE: This test is minimal as the method's logic is currently disabled.
    """
    # Arrange
    issue = {"number": 123, "title": "Test Issue"}

    # Act & Assert
    # The method is called to ensure it runs without raising exceptions.
    # No assertion is needed as the method currently returns None.
    task_service.request_task(issue)
