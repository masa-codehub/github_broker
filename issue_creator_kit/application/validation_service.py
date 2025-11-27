import frontmatter

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
        try:
            post = frontmatter.load(file_path)
        except Exception as e:
            raise FrontmatterError(f"Frontmatter is missing or invalid in {file_path}.") from e

        if not isinstance(post.metadata, dict):
            raise FrontmatterError("Frontmatter is not a valid dictionary.")

        metadata = post.metadata

        # 必須フィールド 'title' の検証
        if 'title' not in metadata:
            raise FrontmatterError("Required 'title' field is missing in frontmatter.")

        title = metadata['title']
        if not isinstance(title, str):
            raise FrontmatterError("Required 'title' field must be a string.")
        if not title.strip():
            raise FrontmatterError("Required 'title' field cannot be empty.")

        # 推奨フィールド 'labels' の型検証
        if 'labels' in metadata and not (
            isinstance(metadata['labels'], list) and
            all(isinstance(label, str) for label in metadata['labels'])
        ):
            raise FrontmatterError("'labels' field must be a list of strings.")

        # 推奨フィールド 'related_issues' の型検証
        if 'related_issues' in metadata and not (
            isinstance(metadata['related_issues'], list) and
            all(isinstance(issue, int) for issue in metadata['related_issues'])
        ):
            raise FrontmatterError("'related_issues' field must be a list of integers.")
