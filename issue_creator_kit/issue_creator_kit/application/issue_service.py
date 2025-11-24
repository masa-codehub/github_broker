import yaml

from issue_creator_kit.domain.issue import IssueData


def _sanitize_string_list(data: object) -> list[str]:
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, str)]


def parse_issue_content(content: str) -> IssueData | None:
    """
    ファイルコンテンツからイシューデータ（タイトル、本文、ラベル、担当者）を抽出します。

    パラメータ:
        content (str): 解析対象のファイルコンテンツ。YAML Front Matter（---で囲まれた部分）の後にMarkdown本文が続く形式である必要があります。
            例:
                ---
                title: "サンプルイシュー"
                labels: ["bug", "urgent"]
                assignees: ["user1"]
                ---
                これはイシューの本文です。

    戻り値:
        IssueData | None: 抽出されたイシューデータ（タイトル、本文、ラベル、担当者）を含むIssueDataインスタンス。
            フロントマターが無効または必須項目（title）が不足している場合はNoneを返します。

    期待されるフォーマット:
        - ファイルの先頭に'---'で囲まれたYAML Front Matterがあり、その後にMarkdown形式の本文が続くこと。
        - YAML Front Matterには少なくとも'title'キーが必要です。'labels'および'assignees'は省略可能です（省略時は空リスト）。

    例:
        >>> content = '''---
        ... title: "Sample Issue"
        ... labels: ["bug"]
        ... assignees: ["alice"]
        ... ---
        ... Issue body here.
        ... '''
        >>> data = parse_issue_content(content)
        >>> data.title
        'Sample Issue'
        >>> data.body
        'Issue body here.'
        >>> data.labels
        ['bug']
        >>> data.assignees
        ['alice']

        # フロントマターが無効な場合
        >>> invalid_content = 'No front matter here'
        >>> parse_issue_content(invalid_content) is None
        True
    """
    parts = content.split('---', 2) # Split into at most 3 parts: before first ---, front matter, body

    if len(parts) < 3: # Not enough parts for YAML Front Matter
        return None

    # First part is empty, second part is YAML Front Matter
    front_matter_str = parts[1].strip()
    body = parts[2].strip()

    try:
        metadata = yaml.safe_load(front_matter_str)
    except yaml.YAMLError:
        return None

    if not isinstance(metadata, dict):
        return None

    title = metadata.get('title')
    if not isinstance(title, str) or not title.strip():
        return None

    labels = _sanitize_string_list(metadata.get('labels'))
    assignees = _sanitize_string_list(metadata.get('assignees'))

    return IssueData(title=title, body=body, labels=labels, assignees=assignees)
