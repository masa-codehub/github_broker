from dataclasses import dataclass, field


@dataclass
class IssueData:
    """
    データクラス: GitHubイシューのメタデータとボディを保持します。

    Attributes:
        title: イシューのタイトル
        body: イシューの本文（Markdown形式）
        labels: ラベルのリスト
        assignees: アサイン先ユーザー名のリスト
    """
    title: str
    body: str
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
