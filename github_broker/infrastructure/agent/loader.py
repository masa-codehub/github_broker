from pathlib import Path

import yaml

from github_broker.domain.agent_config import AgentConfig


class AgentConfigLoader:
    """
    Loads and validates agent configuration from a YAML file.
    """
    def __init__(self, config_path: Path):
        self.config_path = config_path

    def load_config(self) -> AgentConfig:
        """
        Loads the YAML file, validates it against the AgentConfig model,
        and returns the validated AgentConfig object.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            yaml.YAMLError: If the file content is not valid YAML syntax.
            ValidationError: If the YAML content does not conform to the Pydantic model.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Agent configuration file not found at: {self.config_path}")

        with open(self.config_path, encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        # Pydanticによる検証
        return AgentConfig.model_validate(raw_config)

