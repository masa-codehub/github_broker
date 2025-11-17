import os

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentDefinition(BaseModel):
    """エージェントの定義を表すPydanticモデル。"""

    role: str = Field(..., description="The role of the agent.")
    description: str = Field(..., description="The description of the agent.")


class Settings(BaseSettings):
    # Pydantic-settingsの設定
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Docker Secretsのパスを指定
        secrets_dir="/run/secrets" if os.path.exists("/run/secrets") else None,
        extra="ignore",
    )

    # 機密情報 (Docker Secretsから読み込む)
    GITHUB_TOKEN: str

    BROKER_PORT: int = 8000
    GITHUB_REPOSITORY: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    GITHUB_INDEXING_WAIT_SECONDS: int = 15
    TESTING: bool = False
    POLLING_INTERVAL_SECONDS: int = 5 * 60
    LONG_POLLING_CHECK_INTERVAL: int = 5
    FIX_TASK_REDIS_TIMEOUT: int = 86400
    GEMINI_EXECUTOR_PROMPT_FILE: str = (
        "github_broker/infrastructure/prompts/gemini_executor.yml"
    )
    AGENT_DEFINITIONS: list[AgentDefinition] = []
