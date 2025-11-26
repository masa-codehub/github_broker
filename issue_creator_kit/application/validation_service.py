import os
from typing import Any

import yaml

from issue_creator_kit.application.exceptions import ValidationError


def _validate_optional_list_field(
    frontmatter: dict[str, Any],
    field_name: str,
    element_type: type,
    error_message_type: str,
    error_message_element: str,
) -> None:
    """オプションのリストフィールドを検証するヘルパー関数"""
    field_value = frontmatter.get(field_name)
    if field_value is not None:
        if not isinstance(field_value, list):
            raise ValidationError(error_message_type)
        for item in field_value:
            if not isinstance(item, element_type):
                raise ValidationError(error_message_element)

def validate_frontmatter(file_path: str) -> None:
    """
    Markdownファイルのフロントマターを検証する。

    Args:
        file_path (str): 検証するMarkdownファイルのパス。

    Returns:
        None: 検証が成功した場合、何も返しません。

    Raises:
        FileNotFoundError: ファイルが存在しない場合。
        ValidationError: 検証ルールに違反した場合。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    # フロントマターはファイルの先頭から始まる必要がある
    if not content.startswith('---'):
        raise ValidationError("フロントマターはファイルの先頭から '---' で始まる必要があります。")

    frontmatter_end = content.find('---', 3)
    if frontmatter_end == -1:
        raise ValidationError("フロントマターの終了区切りが見つかりませんでした。")

    frontmatter_str = content[3:frontmatter_end].strip()

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        raise ValidationError(f"フロントマターの解析に失敗しました: {e}") from e

    if not isinstance(frontmatter, dict):
        # 空のフロントマター (`--- ---`) の場合、frontmatterはNoneになる
        if frontmatter is None:
            frontmatter = {}
        else:
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
    _validate_optional_list_field(
        frontmatter,
        'labels',
        str,
        "labelsフィールドは文字列のリストである必要があります。",
        "labelsフィールドの全ての要素は文字列である必要があります。",
    )

    # related_issuesフィールドの検証（オプション）
    _validate_optional_list_field(
        frontmatter,
        'related_issues',
        int,
        "related_issuesフィールドは数値のリストである必要があります。",
        "related_issuesフィールドの全ての要素は整数である必要があります。",
    )
