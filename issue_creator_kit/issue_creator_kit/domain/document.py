from enum import Enum, auto
from types import MappingProxyType


class DocumentType(Enum):
    ADR = auto()
    DESIGN_DOC = auto()
    PLAN = auto()
    IN_BOX = auto()


PLAN_HEADERS = [
    "## 親Issue (Parent Issue)",
    "## 子Issue (Sub-Issues)",
    "## As-is (現状)",
    "## To-be (あるべき姿)",
    "## 完了条件 (Acceptance Criteria)",
    "## 成果物 (Deliverables)",
    "## ブランチ戦略 (Branching Strategy)",
]

REQUIRED_HEADERS = MappingProxyType(
    {
        DocumentType.ADR: [
            "# 概要 / Summary",
            "- Status:",
            "- Date:",
            "## 状況 / Context",
            "## 決定 / Decision",
            "## 結果 / Consequences",
            "### メリット (Positive consequences)",
            "### デメリット (Negative consequences)",
            "## 検証基準 / Verification Criteria",
            "## 実装状況 / Implementation Status",
        ],
        DocumentType.DESIGN_DOC: [
            "# 概要 / Overview",
            "## 背景と課題 / Background",
            "## ゴール / Goals",
            "### 機能要件 / Functional Requirements",
            "### 非機能要件 / Non-Functional Requirements",
            "## 設計 / Design",
            "### ハイレベル設計 / High-Level Design",
            "### 詳細設計 / Detailed Design",
            "## 検討した代替案 / Alternatives Considered",
            "## セキュリティとプライバシー / Security & Privacy",
            "## 未解決の問題 / Open Questions & Unresolved Issues",
            "## 検証基準 / Verification Criteria",
            "## 実装状況 / Implementation Status",
        ],
        DocumentType.PLAN: PLAN_HEADERS,
        DocumentType.IN_BOX: PLAN_HEADERS,
    }
)
