
import pytest

from issue_creator_kit.application.exceptions import ValidationError
from issue_creator_kit.application.validation_service import validate_frontmatter


# テスト用のダミーファイルを作成するフィクスチャ
@pytest.fixture
def dummy_md_file(tmp_path):
    def _create_file(filename, content):
        file_path = tmp_path / filename
        file_path.write_text(content)
        return str(file_path)
    return _create_file

class TestValidationService:
    def test_validate_frontmatter_no_frontmatter_raises_error(self, dummy_md_file):
        """
        フロントマターがないMarkdownファイルがValidationErrorを送出することを確認
        """
        file_content = "This is a markdown file with no frontmatter."
        file_path = dummy_md_file("no_frontmatter.md", file_content)

        with pytest.raises(ValidationError, match="フロントマターが見つかりませんでした。"):
            validate_frontmatter(file_path)

    def test_validate_frontmatter_no_title_raises_error(self, dummy_md_file):
        """
        titleフィールドがないMarkdownファイルがValidationErrorを送出することを確認
        """
        file_content = """---
labels: ["bug"]
---
# Issue
"""
        file_path = dummy_md_file("no_title.md", file_content)

        with pytest.raises(ValidationError, match="titleフィールドが見つかりません。"):
            validate_frontmatter(file_path)

    def test_validate_frontmatter_empty_title_raises_error(self, dummy_md_file):
        """
        titleフィールドが空文字列のMarkdownファイルがValidationErrorを送出することを確認
        """
        file_content = """---
title: ""
labels: ["bug"]
---
# Issue
"""
        file_path = dummy_md_file("empty_title.md", file_content)

        with pytest.raises(ValidationError, match="titleフィールドは空にできません。"):
            validate_frontmatter(file_path)

    def test_validate_frontmatter_labels_not_list_raises_error(self, dummy_md_file):
        """
        labelsフィールドがリストではないMarkdownファイルがValidationErrorを送出することを確認
        """
        file_content = """---
title: "Test Title"
labels: "bug"
---
# Issue
"""
        file_path = dummy_md_file("labels_not_list.md", file_content)

        with pytest.raises(ValidationError, match="labelsフィールドは文字列のリストである必要があります。"):
            validate_frontmatter(file_path)

    def test_validate_frontmatter_labels_elements_not_string_raises_error(self, dummy_md_file):
        """
        labelsフィールドの要素が文字列ではないMarkdownファイルがValidationErrorを送出することを確認
        """
        file_content = """---
title: "Test Title"
labels: ["bug", 123]
---
# Issue
"""
        file_path = dummy_md_file("labels_elements_not_string.md", file_content)

        with pytest.raises(ValidationError, match="labelsフィールドの全ての要素は文字列である必要があります。"):
            validate_frontmatter(file_path)

    def test_validate_frontmatter_related_issues_not_list_raises_error(self, dummy_md_file):
        """
        related_issuesフィールドがリストではないMarkdownファイルがValidationErrorを送出することを確認
        """
        file_content = """---
title: "Test Title"
related_issues: 123
---
# Issue
"""
        file_path = dummy_md_file("related_issues_not_list.md", file_content)

        with pytest.raises(ValidationError, match="related_issuesフィールドは数値のリストである必要があります。"):
            validate_frontmatter(file_path)

    def test_validate_frontmatter_related_issues_elements_not_int_raises_error(self, dummy_md_file):
        """
        related_issuesフィールドの要素が数値ではないMarkdownファイルがValidationErrorを送出することを確認
        """
        file_content = """---
title: "Test Title"
related_issues: [123, "abc"]
---
# Issue
"""
        file_path = dummy_md_file("related_issues_elements_not_int.md", file_content)

        with pytest.raises(ValidationError, match="related_issuesフィールドの全ての要素は数値である必要があります。"):
            validate_frontmatter(file_path)

    def test_validate_frontmatter_valid_frontmatter_passes(self, dummy_md_file):
        """
        有効なフロントマターを持つMarkdownファイルがエラーを送出しないことを確認
        """
        file_content = """---
title: "Valid Title"
labels: ["feature", "P0"]
related_issues: [1, 2]
---
# Valid Issue
"""
        file_path = dummy_md_file("valid_frontmatter.md", file_content)

        try:
            validate_frontmatter(file_path)
        except ValidationError as e:
            pytest.fail(f"ValidationError was raised unexpectedly: {e}")

    def test_validate_frontmatter_optional_fields_missing_passes(self, dummy_md_file):
        """
        labelsとrelated_issuesフィールドが省略されていてもエラーを送出しないことを確認
        """
        file_content = """---
title: "Another Valid Title"
---
# Another Valid Issue
"""
        file_path = dummy_md_file("optional_fields_missing.md", file_content)

        try:
            validate_frontmatter(file_path)
        except ValidationError as e:
            pytest.fail(f"ValidationError was raised unexpectedly: {e}")
