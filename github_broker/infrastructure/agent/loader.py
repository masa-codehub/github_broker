from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, cast

from github_broker.domain.agent_config import AgentConfigList


class AgentConfigLoader:
    @staticmethod
    def load_from_file(filepath: str | Path) -> AgentConfigList:
        """Loads agent configurations from a TOML file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Agent config file not found at {filepath}")

        with path.open("rb") as f:
            data = tomllib.load(f)
        return AgentConfigList.model_validate(data)

    @staticmethod
    def load_from_dict(data: dict[str, Any]) -> AgentConfigList:
        """Loads agent configurations from a dictionary."""
        return AgentConfigList.model_validate(cast(dict[str, Any], data))
