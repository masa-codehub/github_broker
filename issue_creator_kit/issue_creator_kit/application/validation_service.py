import re

import frontmatter

from ..domain.document import REQUIRED_HEADERS, DocumentType
from .exceptions import FrontmatterError


class ValidationService:
    """
    ドキュメントの検証に関するビジネスロジックを提供するサービスクラス。
    """

    VALID_ROLES = {
        'PRODUCT_MANAGER', 'TECHNICAL_DESIGNER', 'BACKENDCODER', 'FRONTENDCODER',
        'UIUX_DESIGNER', 'CODE_REVIEWER', 'CONTENTS_WRITER', 'MARKET_RESEARCHER',
        'PEST_ANALYST', 'SYSTEM_ARCHITECT'
    }

    MSG_BRANCH_BASE_MISSING = "Branching Strategy section must contain 'ベースブランチ (Base Branch):'"
    MSG_BRANCH_FEATURE_MISSING = "Branching Strategy section must contain '作業ブランチ (Feature Branch):'"
    MSG_EPIC_CRITERIA_MISSING = "Epic completion criteria must contain 'このEpicを構成する全てのStoryの実装が完了していること。'"
    MSG_STORY_CRITERIA_MISSING = "Story completion criteria must contain 'このStoryを構成する全てのTaskの実装が完了していること。'"
    MSG_TASK_CRITERIA_MISSING = "Task completion criteria must contain 'TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。'"

    def validate_frontmatter(self, file_path: str) -> dict:
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

        if 'labels' in metadata:
            labels = metadata['labels']
            if not (isinstance(labels, list) and all(isinstance(label, str) for label in labels)):
                raise FrontmatterError(f"'labels' field must be a list of strings in {file_path}.")

            if not any(label in labels for label in ['epic', 'story', 'task']):
                raise FrontmatterError(f"'labels' must contain one of 'epic', 'story', 'task' in {file_path}.")

            if not any(re.match(r'^P[0-4]$', label) for label in labels):
                raise FrontmatterError(f"'labels' must contain a priority label (P0-P4) in {file_path}.")

            if not any(label in self.VALID_ROLES for label in labels):
                raise FrontmatterError(f"'labels' must contain a valid agent role label (e.g., BACKENDCODER) in {file_path}.")

        if 'related_issues' in metadata and not (isinstance(metadata['related_issues'], list) and all(isinstance(issue, int) for issue in metadata['related_issues'])):
            raise FrontmatterError(f"'related_issues' field must be a list of integers in {file_path}.")

        return metadata

    def validate_plan_content(self, content: str, metadata: dict) -> list[str]:
        """計画ファイルのコンテンツ内容を検証します。"""
        errors = []
        labels = metadata.get('labels', [])

        # Branch Strategy check
        branch_section = re.search(r"## ブランチ戦略 \(Branching Strategy\)(.*?)(\n## |$)", content, re.DOTALL)
        if branch_section:
            section_text = branch_section.group(1)
            if "ベースブランチ (Base Branch):" not in section_text:
                errors.append(self.MSG_BRANCH_BASE_MISSING)
            if "作業ブランチ (Feature Branch):" not in section_text:
                errors.append(self.MSG_BRANCH_FEATURE_MISSING)

        # Completion Criteria check
        criteria_section = re.search(r"## 完了条件 \(Acceptance Criteria\)(.*?)(\n## |$)", content, re.DOTALL)
        if criteria_section:
            section_text = criteria_section.group(1)
            if 'epic' in labels and "このEpicを構成する全てのStoryの実装が完了していること。" not in section_text:
                errors.append(self.MSG_EPIC_CRITERIA_MISSING)
            if 'story' in labels and "このStoryを構成する全てのTaskの実装が完了していること。" not in section_text:
                errors.append(self.MSG_STORY_CRITERIA_MISSING)
            if 'task' in labels and "TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。" not in section_text:
                errors.append(self.MSG_TASK_CRITERIA_MISSING)

        return errors

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
