
from pydantic import BaseModel, Field


class AgentDefinition(BaseModel):
    """
    エージェントの役割と説明を定義するPydanticモデル。
    これは、外部YAMLファイルから読み込まれるエージェント設定の各エントリに対応します。
    """

    role: str = Field(..., description="エージェントの役割名 (例: BACKENDCODER)")
    description: str = Field(..., description="エージェントの役割の説明")


class AgentConfigList(BaseModel):
    """
    エージェント設定ファイル全体の構造を定義するPydanticモデル。
    """

    agents: list[AgentDefinition] = Field(
        ..., description="定義されたエージェントのリスト"
    )
