import re

import frontmatter

from ..domain.document import REQUIRED_HEADERS, DocumentType
from .exceptions import FrontmatterError


class ValidationService:
    """
    ドキュメントの検証に関するビジネスロジックを提供するサービスクラス。
    """

    def validate_frontmatter(self, file_path: str):
        """
        指定されたMarkdownファイルのフロントマターを検証する。
        """
        try:
            post = frontmatter.load(file_path)
        except Exception as e:
            raise FrontmatterError(f"Frontmatter is missing or invalid in {file_path}.") from e

        if not post.metadata:
             raise FrontmatterError(f"Frontmatter is missing or invalid in {file_path}.")

        if not isinstance(post.metadata, dict):
            raise FrontmatterError(f"Frontmatter is not a valid dictionary in {file_path}.")

        metadata = post.metadata
        if 'title' not in metadata:
            raise FrontmatterError(f"Required 'title' field is missing in frontmatter in {file_path}.")

        title = metadata['title']
        if not isinstance(title, str):
            raise FrontmatterError(f"Required 'title' field must be a string in {file_path}.")
        if not title.strip():
            raise FrontmatterError(f"Required 'title' field cannot be empty in {file_path}.")

        if 'labels' in metadata and not (isinstance(metadata['labels'], list) and all(isinstance(label, str) for label in metadata['labels'])):
            raise FrontmatterError(f"'labels' field must be a list of strings in {file_path}.")
        if 'related_issues' in metadata and not (isinstance(metadata['related_issues'], list) and all(isinstance(issue, int) for issue in metadata['related_issues'])):
            raise FrontmatterError(f"'related_issues' field must be a list of integers in {file_path}.")

    def _extract_headers_from_content(self, content: str) -> list[str]:
        """Markdownコンテンツから `#`, `##`, `###` で始まるヘッダーを抽出します。"""
        headers = re.findall(r"^(#{1,3})\s+(.*)$", content, re.MULTILINE)
        return [f"{level} {title.strip()}" for level, title in headers]

    def validate_sections(self, content: str, doc_type: DocumentType) -> list[str]:
        """ドキュメントに必要なセクションが含まれているか検証します。"""
        required_headers = REQUIRED_HEADERS.get(doc_type, [])
        if not required_headers:
            return []

        present_headers = set(self._extract_headers_from_content(content))
        present_content_lines = {line.strip() for line in content.splitlines()}
        missing = []
        for header in required_headers:
            if header.startswith("#"):
                if header not in present_headers:
                    missing.append(header)
            else:
                if not any(line.startswith(header) for line in present_content_lines):
                    missing.append(header)
        return missing

    def validate_adr_summary_format(self, content: str) -> bool:
        """ADRの概要セクションのフォーマットを検証します。"""
        pattern = r"^# 概要 / Summary\s*\[ADR-\d+\]"
        return bool(re.search(pattern, content, re.MULTILINE | re.DOTALL))

    def validate_design_doc_overview(self, content: str) -> bool:
        """Design Docの概要セクションのフォーマットを検証します。"""
        pattern = r"^# 概要 / Overview\n[ \t]*デザインドキュメント:"
        return bool(re.search(pattern, content, re.MULTILINE))
