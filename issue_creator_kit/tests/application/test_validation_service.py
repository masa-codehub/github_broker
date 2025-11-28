from pathlib import Path

import pytest

from issue_creator_kit.application.exceptions import FrontmatterError
from issue_creator_kit.application.validation_service import ValidationService
from issue_creator_kit.domain.document import DocumentType


# pytest.mark.parametrize を使用して、可読性とメンテナンス性を向上
@pytest.mark.parametrize(
    "file_content, expected_exception, error_message",
    [
        # Existing tests
        ("no frontmatter here", FrontmatterError, "Frontmatter is missing or invalid."),
        ("---\n---\nno title", FrontmatterError, "Required 'title' field is missing in frontmatter."),
        ("--- \ntitle: ''\n--- \nempty title", FrontmatterError, "Required 'title' field cannot be empty."),
        ("--- \ntitle: 'Valid Title'\nlabels: 'not-a-list'\n--- \n", FrontmatterError, "'labels' field must be a list of strings."),
        ("--- \ntitle: 'Valid Title'\nrelated_issues: ['not-a-number']\n--- \n", FrontmatterError, "'related_issues' field must be a list of integers."),

        # New tests from review
        ("--- \ntitle: '   '\n--- \nwhitespace title", FrontmatterError, "Required 'title' field cannot be empty."),
        ("\n--- \ntitle: 'Valid'\n--- \n", FrontmatterError, "Frontmatter is missing or invalid."),
        ("--- \ntitle: [invalid yaml\n--- \n", FrontmatterError, "Frontmatter is missing or invalid."),
        ("--- \ntitle: 'Valid'\nlabels: ['bug', 123]\n--- \n", FrontmatterError, "'labels' field must be a list of strings."),
        ("--- \ntitle: 'Valid'\nrelated_issues: [123, 1.23]\n--- \n", FrontmatterError, "'related_issues' field must be a list of integers."),
        ("--- \ntitle: 123\n--- \n", FrontmatterError, "Required 'title' field must be a string."),

        # Test case for frontmatter as a list
        (
            "--- \n- item1\n- item2\n--- \n",
            FrontmatterError,
            "Frontmatter is not a valid dictionary.",
        ),

        # Valid case
        ("--- \ntitle: 'Valid Title'\nlabels: ['bug', 'P1']\nrelated_issues: [123, 456]\n--- \nValid content", None, None),
    ],
)
def test_validate_frontmatter(tmp_path: Path, file_content: str, expected_exception, error_message):
    """
    ADR-019で定義されたフロントマターの検証ルールをテストする。
    """
    # テスト用のMarkdownファイルを動的に生成
    p = tmp_path / "test_document.md"
    p.write_text(file_content)

    # サービスインスタンスを作成
    service = ValidationService()

    if expected_exception:
        # 例外が送出されることを確認
        with pytest.raises(expected_exception) as excinfo:
            service.validate_frontmatter(str(p))
        # エラーメッセージが期待通りであることを確認
        assert error_message in str(excinfo.value)
    else:
        # 例外が送出されないことを確認
        try:
            service.validate_frontmatter(str(p))
        except FrontmatterError as e:
            pytest.fail(f"Unexpected exception raised: {e}")

# Test for _extract_headers_from_content
def test_extract_headers_from_content():
    service = ValidationService()
    content = """
# Header 1
Some text.
## Header 2
### Header 3
- Not a header
"""
    headers = service._extract_headers_from_content(content)
    assert headers == ["# Header 1", "## Header 2", "### Header 3"]

def test_extract_headers_from_content_all_levels():
    service = ValidationService()
    content = """
# Title 1
## Title 2
### Title 3
#### Title 4
"""
    expected_headers = [
        "# Title 1",
        "## Title 2",
        "### Title 3",
    ]
    assert service._extract_headers_from_content(content) == expected_headers

def test_extract_headers_from_content_no_headers():
    service = ValidationService()
    content = """
No double-sharp headers here.
"""
    assert service._extract_headers_from_content(content) == []

# Tests for validate_sections
@pytest.fixture
def valid_adr_content():
    return """
# 概要 / Summary
[ADR-001]

- Status: Proposed
- Date: 2023-10-26

## 状況 / Context
Some context here.

## 決定 / Decision
Some decision here.

## 結果 / Consequences
### メリット (Positive consequences)
- Pro 1
### デメリット (Negative consequences)
- Con 1

## 検証基準 / Verification Criteria
Verification criteria.

## 実装状況 / Implementation Status
Implementation status.
"""

@pytest.fixture
def invalid_adr_content():
    return """
# 概要 / Summary
[ADR-001]

- Status: Proposed
- Date: 2023-10-26

## 状況 / Context
Some context here.

## 決定 / Decision
Some decision here.

## 結果 / Consequences
### メリット (Positive consequences)
- Pro 1
"""

@pytest.fixture
def invalid_adr_content_missing_meta():
    return """
# 概要 / Summary
[ADR-001]

## 状況 / Context
Some context here.

## 決定 / Decision
Some decision here.

## 結果 / Consequences
### メリット (Positive consequences)
- Pro 1

### デメリット (Negative consequences)
- Con 1

## 検証基準 / Verification Criteria
Verification criteria.

## 実装状況 / Implementation Status
Implementation status.
"""

@pytest.fixture
def valid_design_doc_content():
    return """
# 概要 / Overview
デザインドキュメント: This is a test design document.

## 背景と課題 / Background
Background and issues.

## ゴール / Goals
### 機能要件 / Functional Requirements
- Requirement 1
### 非機能要件 / Non-Functional Requirements
- Requirement 2

## 設計 / Design
### ハイレベル設計 / High-Level Design
High-level design.
### 詳細設計 / Detailed Design
Detailed design.

## 検討した代替案 / Alternatives Considered
Alternatives.

## セキュリティとプライバシー / Security & Privacy
Security and privacy considerations.

## 未解決の問題 / Open Questions & Unresolved Issues
Open questions.

## 検証基準 / Verification Criteria
Verification criteria.

## 実装状況 / Implementation Status
Implementation status.
"""

def test_validate_sections_valid_adr(valid_adr_content):
    service = ValidationService()
    missing = service.validate_sections(valid_adr_content, DocumentType.ADR)
    assert not missing, f"Missing headers: {missing}"

def test_validate_sections_valid_design_doc(valid_design_doc_content):
    service = ValidationService()
    missing = service.validate_sections(valid_design_doc_content, DocumentType.DESIGN_DOC)
    assert not missing, f"Missing headers: {missing}"

def test_validate_sections_invalid(invalid_adr_content):
    service = ValidationService()
    missing = service.validate_sections(invalid_adr_content, DocumentType.ADR)
    assert "### デメリット (Negative consequences)" in missing
    assert "## 検証基準 / Verification Criteria" in missing
    assert "## 実装状況 / Implementation Status" in missing

def test_validate_sections_invalid_missing_meta(invalid_adr_content_missing_meta):
    service = ValidationService()
    missing = service.validate_sections(invalid_adr_content_missing_meta, DocumentType.ADR)
    assert "- Status:" in missing
    assert "- Date:" in missing

# Tests for validate_adr_summary_format
@pytest.mark.parametrize(
    "content, expected",
    [
        pytest.param(
            "# 概要 / Summary\n[ADR-123] This is a title",
            True,
            id="success_basic",
        ),
        pytest.param(
            "# 概要 / Summary\n\n[ADR-1] Another title",
            True,
            id="success_with_newline",
        ),
        pytest.param(
            "# 概要 / Summary\n   \n[ADR-1] Another title",
            True,
            id="success_with_whitespace_and_newline",
        ),
        pytest.param(
            "# 概要 / Summary\nThis is not a valid summary format.",
            False,
            id="failure_invalid_format",
        ),
        pytest.param(
            "Some other content\n# Not the summary",
            False,
            id="failure_no_summary_header",
        ),
        pytest.param(
            "# 概要 / Summary",
            False,
            id="failure_header_only",
        ),
        pytest.param(
            "# 概要 / Summary\n\n",
            False,
            id="failure_header_with_newlines_only",
        ),
        pytest.param(
            "# 概要 / Summary\n[ADR-abc]",
            False,
            id="failure_non_digit_in_adr_number",
        ),
    ],
)
def test_validate_adr_summary_format(content, expected):
    service = ValidationService()
    assert service.validate_adr_summary_format(content) == expected

# Tests for validate_design_doc_overview
def test_validate_design_doc_overview_success():
    service = ValidationService()
    content = """
# 概要 / Overview
デザインドキュメント: test
"""
    assert service.validate_design_doc_overview(content) is True

def test_validate_design_doc_overview_success_with_whitespace():
    service = ValidationService()
    content = """
# 概要 / Overview
  デザインドキュメント: test
"""
    assert service.validate_design_doc_overview(content) is True

def test_validate_design_doc_overview_success_no_extra_text():
    service = ValidationService()
    content = """
# 概要 / Overview
デザインドキュメント:
"""
    assert service.validate_design_doc_overview(content) is True

def test_validate_design_doc_overview_failure():
    service = ValidationService()
    content = """
# 概要 / Overview
これはデザインドキュメントです
"""
    assert service.validate_design_doc_overview(content) is False

def test_validate_design_doc_overview_failure_not_at_start():
    service = ValidationService()
    content = """
# 概要 / Overview
これは デザインドキュメント: です
"""
    assert service.validate_design_doc_overview(content) is False

def test_validate_design_doc_overview_failure_with_newline():
    service = ValidationService()
    content = """
# 概要 / Overview

デザインドキュメント: test
"""
    assert service.validate_design_doc_overview(content) is False

def test_validate_design_doc_overview_no_overview():
    service = ValidationService()
    content = """
## ゴール / Goals
"""
    assert service.validate_design_doc_overview(content) is False
