from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

from github_broker.domain.agent_config import AgentConfigList


class AgentConfigLoader:
    @staticmethod
    def load_from_file(filepath: str | Path) -> AgentConfigList:
        """Loads agent configurations from a YAML file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Agent config file not found at {filepath}")

        with path.open("r") as f:
            data = yaml.safe_load(f)
        return AgentConfigList.model_validate(data)

    @staticmethod
    def load_from_dict(data: dict[str, Any]) -> AgentConfigList:
        """Loads agent configurations from a dictionary."""
        return AgentConfigList.model_validate(cast(dict[str, Any], data))
