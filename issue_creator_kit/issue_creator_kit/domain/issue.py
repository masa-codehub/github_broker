
class IssueData:
    """
    データクラス: GitHubイシューのメタデータとボディを保持します。

    Attributes:
        title: イシューのタイトル
        body: イシューの本文（Markdown形式）
        labels: ラベルのリスト
        assignees: アサイン先ユーザー名のリスト
    """
    def __init__(self, title: str, body: str, labels: list[str] | None = None, assignees: list[str] | None = None):
        self.title = title
        self.body = body
        self.labels = labels if labels is not None else []
        self.assignees = assignees if assignees is not None else []
