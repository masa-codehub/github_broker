import os

import yaml

from issue_creator_kit.application.exceptions import ValidationError


def validate_frontmatter(file_path: str):
    """
    Markdownファイルのフロントマターを検証する。

    Args:
        file_path (str): 検証するMarkdownファイルのパス。

    Raises:
        ValidationError: 検証ルールに違反した場合。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    # フロントマターのパース
    # --- で始まり、--- で終わるブロックを探す
    frontmatter_start = content.find('---')
    if frontmatter_start == -1:
        raise ValidationError("フロントマターが見つかりませんでした。")

    frontmatter_end = content.find('---', frontmatter_start + 3)
    if frontmatter_end == -1:
        raise ValidationError("フロントマターの終了区切りが見つかりませんでした。")

    frontmatter_str = content[frontmatter_start + 3:frontmatter_end].strip()

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        raise ValidationError(f"フロントマターの解析に失敗しました: {e}") from e

    if not isinstance(frontmatter, dict):
        raise ValidationError("フロントマターはYAML形式のキーバリューペアである必要があります。")

    # titleフィールドの検証
    title = frontmatter.get('title')
    if title is None:
        raise ValidationError("titleフィールドが見つかりません。")
    if not isinstance(title, str):
        raise ValidationError("titleフィールドは文字列である必要があります。")
    if not title.strip():
        raise ValidationError("titleフィールドは空にできません。")

    # labelsフィールドの検証（オプション）
    labels = frontmatter.get('labels')
    if labels is not None:
        if not isinstance(labels, list):
            raise ValidationError("labelsフィールドは文字列のリストである必要があります。")
        for label in labels:
            if not isinstance(label, str):
                raise ValidationError("labelsフィールドの全ての要素は文字列である必要があります。")

    # related_issuesフィールドの検証（オプション）
    related_issues = frontmatter.get('related_issues')
    if related_issues is not None:
        if not isinstance(related_issues, list):
            raise ValidationError("related_issuesフィールドは数値のリストである必要があります。")
        for issue_id in related_issues:
            if not isinstance(issue_id, int | float): # intまたはfloatを許可
                raise ValidationError("related_issuesフィールドの全ての要素は数値である必要があります。")
