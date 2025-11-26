from pathlib import Path

import yaml

from .exceptions import FrontmatterError


class ValidationService:
    """
    ドキュメントの検証に関するビジネスロジックを提供するサービスクラス。
    """

    def validate_frontmatter(self, file_path: str):
        """
        指定されたMarkdownファイルのフロントマターを検証する。

        Args:
            file_path: 検証するファイルのパス。

        Raises:
            FrontmatterError: フロントマターが存在しない、形式が不正、
                              または必須フィールドが不足している場合に送出される。
        """
        p = Path(file_path)
        try:
            # ファイルの内容を読み込み、フロントマター部分を抽出
            content = p.read_text()
            if not content.startswith('---'):
                raise FrontmatterError("Frontmatter is missing or invalid.")

            parts = content.split('---')
            if len(parts) < 3:
                raise FrontmatterError("Frontmatter is missing or invalid.")

            frontmatter_str = parts[1]
            frontmatter = yaml.safe_load(frontmatter_str) or {}

            if not isinstance(frontmatter, dict):
                 raise FrontmatterError("Frontmatter is not a valid dictionary.")

            # 必須フィールド 'title' の検証
            if 'title' not in frontmatter:
                raise FrontmatterError("Required 'title' field is missing in frontmatter.")
            if not frontmatter['title']:
                raise FrontmatterError("Required 'title' field cannot be empty.")

            # 推奨フィールド 'labels' の型検証
            if 'labels' in frontmatter and not (
                isinstance(frontmatter['labels'], list) and
                all(isinstance(label, str) for label in frontmatter['labels'])
            ):
                raise FrontmatterError("'labels' field must be a list of strings.")

            # 推奨フィールド 'related_issues' の型検証
            if 'related_issues' in frontmatter and not (
                isinstance(frontmatter['related_issues'], list) and
                all(isinstance(issue, int) for issue in frontmatter['related_issues'])
            ):
                raise FrontmatterError("'related_issues' field must be a list of integers.")

        except yaml.YAMLError as e:
            raise FrontmatterError("Frontmatter is missing or invalid.") from e
        except FileNotFoundError:
            raise
