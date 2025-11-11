from __future__ import annotations

from typing import cast

import punq
import redis

from github_broker.application.task_service import TaskService
from github_broker.domain.agent_config import AgentConfigList
from github_broker.infrastructure.agent.loader import AgentConfigLoader
from github_broker.infrastructure.config import Settings, get_settings
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient


def create_container(settings: Settings | None = None) -> punq.Container:
    s = settings or get_settings()

    # Parse owner and repo from repository string
    try:
        owner, repo_name = s.github_agent_repository.split("/")
    except ValueError:
        raise ValueError(
            "github_agent_repository must be in the format 'owner/repo_name'"
        ) from None

    # Create clients with correct arguments
    github_client = GitHubClient(
        github_repository=s.github_agent_repository,
        github_token=s.github_personal_access_token,
    )
    redis_instance = redis.from_url(s.redis_url, decode_responses=True)
    redis_client = RedisClient(redis=redis_instance, owner=owner, repo_name=repo_name)

    # Load agent configurations
    agent_config_loader = AgentConfigLoader()
    agent_definitions = agent_config_loader.load_from_file(s.github_agent_config_file)

    # Build container
    container = punq.Container()
    container.register(Settings, instance=s)
    container.register(GitHubClient, instance=github_client)
    container.register(RedisClient, instance=redis_client)
    container.register(AgentConfigLoader, instance=agent_config_loader)
    container.register(AgentConfigList, instance=cast(AgentConfigList, agent_definitions))
    container.register(
        TaskService,
        factory=lambda: TaskService(
            github_client=container.resolve(GitHubClient),
            redis_client=container.resolve(RedisClient),
            agent_configs=container.resolve(AgentConfigList),
        ),
    )
    return container



