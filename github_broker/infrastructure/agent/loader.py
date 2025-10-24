import yaml
from pathlib import Path
from typing import List

from pydantic import ValidationError

from github_broker.domain.agent_config import AgentDefinition, AgentConfig

class AgentConfigLoader:
    """
    Loads and validates agent configuration from a YAML file.
    """
    def __init__(self, config_path: Path):
        self.config_path = config_path

    def load_config(self) -> List[AgentDefinition]:
        """
        Loads the YAML file, validates it against the AgentConfig model,
        and returns a list of AgentDefinition objects.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            yaml.YAMLError: If the file content is not valid YAML syntax.
            ValidationError: If the YAML content does not conform to the Pydantic model.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Agent configuration file not found at: {self.config_path}")

        with open(self.config_path, 'r') as f:
            raw_config = yaml.safe_load(f)

        # Pydanticによる検証
        validated_config = AgentConfig.model_validate(raw_config)
        return validated_config.agents

