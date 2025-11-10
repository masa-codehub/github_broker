from pydantic import BaseModel, Field


class AgentDefinition(BaseModel):
    """
    単一のエージェントの役割に関する設定を定義します。
    """
    role: str = Field(..., description="エージェントの一意な役割名（例: BACKENDCODER）。")
    description: str = Field(..., description="エージェントの責務に関する簡単な説明。")
    prompt: str | None = Field(None, description="エージェントの完全なシステムプロンプト/ペルソナ。")

class AgentConfig(BaseModel):
    """
    すべてのエージェントのルート設定モデル。
    """
    agents: list[AgentDefinition] = Field(..., description="すべてのエージェント定義のリスト。")
