from typing import TypedDict


class AgentDefinition(TypedDict):
    """エージェントの定義を表すTypedDict。"""

    role: str
    description: str
