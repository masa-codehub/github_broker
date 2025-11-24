
import pytest

from issue_creator_kit.application.validation_service import (
    _extract_headers_from_content,
    validate_adr_summary_format,
    validate_design_doc_overview,
    validate_sections,
)
from issue_creator_kit.domain.document import DocumentType


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
    missing = validate_sections(valid_adr_content, DocumentType.ADR)
    assert not missing, f"Missing headers: {missing}"

def test_validate_sections_valid_design_doc(valid_design_doc_content):
    missing = validate_sections(valid_design_doc_content, DocumentType.DESIGN_DOC)
    assert not missing, f"Missing headers: {missing}"

def test_validate_sections_invalid(invalid_adr_content):
    missing = validate_sections(invalid_adr_content, DocumentType.ADR)
    assert "### デメリット (Negative consequences)" in missing
    assert "## 検証基準 / Verification Criteria" in missing
    assert "## 実装状況 / Implementation Status" in missing

def test_validate_sections_invalid_missing_meta(invalid_adr_content_missing_meta):
    missing = validate_sections(invalid_adr_content_missing_meta, DocumentType.ADR)
    assert "- Status:" in missing
    assert "- Date:" in missing

def test_extract_headers_from_content():
    content = """
# Header 1
Some text.
## Header 2
### Header 3
- Not a header
"""
    headers = _extract_headers_from_content(content)
    assert headers == ["# Header 1", "## Header 2", "### Header 3"]

def test_extract_headers_from_content_all_levels():
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
    assert _extract_headers_from_content(content) == expected_headers

def test_extract_headers_from_content_no_headers():
    content = """
No double-sharp headers here.
"""
    assert _extract_headers_from_content(content) == []

def test_validate_sections_success():
    content = """
## 親Issue (Parent Issue)
## 子Issue (Sub-Issues)
## As-is (現状)
## To-be (あるべき姿)
## 完了条件 (Acceptance Criteria)
## 成果物 (Deliverables)
## ブランチ戦略 (Branching Strategy)
"""
    missing = validate_sections(content, DocumentType.PLAN)
    assert missing == []

def test_validate_sections_missing():
    content = """
## 親Issue (Parent Issue)
## As-is (現状)
## To-be (あるべき姿)
## 完了条件 (Acceptance Criteria)
## 成果物 (Deliverables)
## ブランチ戦略 (Branching Strategy)
"""
    missing = validate_sections(content, DocumentType.PLAN)
    assert missing == ["## 子Issue (Sub-Issues)"]

def test_validate_sections_no_headers():
    content = "No headers here."
    missing = validate_sections(content, DocumentType.PLAN)
    from issue_creator_kit.domain.document import PLAN_HEADERS
    assert missing == PLAN_HEADERS

def test_validate_sections_empty_required():
    content = "## A header"
    # Create a dummy document type that doesn't require headers for this test
    from enum import Enum, auto
    class UnknownType(Enum):
        UNKNOWN = auto()
    missing = validate_sections(content, UnknownType.UNKNOWN)
    assert missing == []

def test_validate_sections_design_doc_missing_new_sections():
    content = """
# 概要 / Overview
デザインドキュメント: test
## ゴール / Goals
## 設計 / Design
"""
    missing = validate_sections(content, DocumentType.DESIGN_DOC)
    assert "## 背景と課題 / Background" in missing
    assert "### 機能要件 / Functional Requirements" in missing
    assert "### 非機能要件 / Non-Functional Requirements" in missing

def test_validate_design_doc_overview_success():
    content = """
# 概要 / Overview
デザインドキュメント: test
"""
    assert validate_design_doc_overview(content) is True

def test_validate_design_doc_overview_success_with_whitespace():
    content = """
# 概要 / Overview
  デザインドキュメント: test
"""
    assert validate_design_doc_overview(content) is True

def test_validate_design_doc_overview_success_no_extra_text():
    content = """
# 概要 / Overview
デザインドキュメント:
"""
    assert validate_design_doc_overview(content) is True

def test_validate_design_doc_overview_failure():
    content = """
# 概要 / Overview
これはデザインドキュメントです
"""
    assert validate_design_doc_overview(content) is False

def test_validate_design_doc_overview_failure_not_at_start():
    content = """
# 概要 / Overview
これは デザインドキュメント: です
"""
    assert validate_design_doc_overview(content) is False

def test_validate_design_doc_overview_failure_with_newline():
    content = """
# 概要 / Overview

デザインドキュメント: test
"""
    assert validate_design_doc_overview(content) is False

def test_validate_design_doc_overview_no_overview():
    content = """
## ゴール / Goals
"""
    assert validate_design_doc_overview(content) is False


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
    assert validate_adr_summary_format(content) == expected
