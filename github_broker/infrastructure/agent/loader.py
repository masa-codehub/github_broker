import logging
from pathlib import Path
from typing import List

import yaml
from pydantic import ValidationError

from github_broker.infrastructure.agent.models import AgentDefinition, AgentConfigList
from github_broker.infrastructure.config import Settings


class AgentConfigLoader:
    """
    エージェント設定ファイル（YAML）を読み込み、バリデーションを行うクラス。
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_config(self) -> List[AgentDefinition]:
        """
        設定ファイルパスからエージェント設定を読み込み、AgentDefinitionのリストを返します。

        Raises:
            FileNotFoundError: 設定ファイルが見つからない場合。
            ValueError: 設定ファイルの形式が不正な場合。
        """
        config_path = Path(self.settings.AGENT_CONFIG_PATH)

        if not config_path.exists():
            error_msg = f"Agent configuration file not found at: {config_path.resolve()}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        self.logger.info(f"Loading agent configuration from: {config_path.resolve()}")

        try:
            with open(config_path, "r") as f:
                raw_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            error_msg = f"Error parsing YAML file at {config_path.resolve()}: {e}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # Pydanticモデルでバリデーション
            validated_config = AgentConfigList.model_validate(raw_config)
            return validated_config.agents
        except ValidationError as e:
            error_msg = f"Agent configuration validation failed for {config_path.resolve()}: {e}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

