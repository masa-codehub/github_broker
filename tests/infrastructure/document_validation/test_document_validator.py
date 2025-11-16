import pytest

from github_broker.infrastructure.document_validation.document_validator import (
    DocumentType,
    _extract_headers_from_content,
    get_required_headers,
    validate_adr_meta,
    validate_adr_summary_format,
    validate_design_doc_overview,
    validate_sections,
)


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
    required_headers = get_required_headers(DocumentType.ADR)
    # Validate headers and metadata separately to ensure both aspects are properly checked
    required_headers_without_meta = [h for h in required_headers if h.startswith("#")]
    missing = validate_sections(valid_adr_content, required_headers_without_meta)
    assert not missing, f"Missing headers: {missing}"
    missing_meta = validate_adr_meta(valid_adr_content)
    assert not missing_meta, f"Missing meta: {missing_meta}"


def test_validate_sections_valid_design_doc(valid_design_doc_content):
    required_headers = get_required_headers(DocumentType.DESIGN_DOC)
    missing = validate_sections(valid_design_doc_content, required_headers)
    assert not missing, f"Missing headers: {missing}"



def test_validate_sections_invalid(invalid_adr_content):
    required_headers = get_required_headers(DocumentType.ADR)
    missing = validate_sections(invalid_adr_content, required_headers)
    assert "### デメリット (Negative consequences)" in missing
    assert "## 検証基準 / Verification Criteria" in missing
    assert "## 実装状況 / Implementation Status" in missing


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
## Section 1
## Section 2
## Section 3
"""
    required_headers = ["## Section 1", "## Section 2"]
    missing = validate_sections(content, required_headers)
    assert missing == []


def test_validate_sections_missing():
    content = """
## Section 1
## Section 3
"""
    required_headers = ["## Section 1", "## Section 2", "## Section 3"]
    missing = validate_sections(content, required_headers)
    assert missing == ["## Section 2"]


def test_validate_sections_no_headers():
    content = "No headers here."
    required_headers = ["## Section 1"]
    missing = validate_sections(content, required_headers)
    assert missing == ["## Section 1"]


def test_validate_sections_empty_required():
    content = "## A header"
    required_headers = []
    missing = validate_sections(content, required_headers)
    assert missing == []


def test_validate_sections_design_doc_missing_new_sections():
    content = """
# 概要 / Overview
デザインドキュメント: test
## ゴール / Goals
## 設計 / Design
"""
    required_headers = get_required_headers(DocumentType.DESIGN_DOC)
    missing = validate_sections(content, required_headers)
    assert "## 背景と課題 / Background" in missing
    assert "### 機能要件 / Functional Requirements" in missing
    assert "### 非機能要件 / Non-Functional Requirements" in missing


@pytest.mark.parametrize(
    "doc_type, expected_headers",
    [
        (DocumentType.ADR, [
            "# 概要 / Summary",
            "## 状況 / Context",
            "## 決定 / Decision",
            "## 結果 / Consequences",
            "### メリット (Positive consequences)",
            "### デメリット (Negative consequences)",
            "## 検証基準 / Verification Criteria",
            "## 実装状況 / Implementation Status",
        ]),
        (DocumentType.DESIGN_DOC, [
            "# 概要 / Overview",
            "## 背景と課題 / Background",
            "## ゴール / Goals",
            "### 機能要件 / Functional Requirements",
            "### 非機能要件 / Non-Functional Requirements",
            "## 設計 / Design",
            "### ハイレベル設計 / High-Level Design",
            "### 詳細設計 / Detailed Design",
            "## 検討した代替案 / Alternatives Considered",
            "## セキュリティとプライバシー / Security & Privacy",
            "## 未解決の問題 / Open Questions & Unresolved Issues",
            "## 検証基準 / Verification Criteria",
            "## 実装状況 / Implementation Status",
        ]),
    ],
)
def test_get_required_headers(doc_type, expected_headers):
    assert get_required_headers(doc_type) == expected_headers


def test_get_required_headers_unknown_type():
    """未知のドキュメントタイプが渡された場合に空のリストを返すことをテストします。"""
    from enum import Enum, auto

    class UnknownType(Enum):
        UNKNOWN = auto()

    assert get_required_headers(UnknownType.UNKNOWN) == []


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


def test_validate_adr_meta_success():
    content = """
- Status: 提案中
- Date: 2025-10-23
"""
    assert validate_adr_meta(content) == []


def test_validate_adr_meta_failure():
    content = """
- state: 提案中
- day: 2025-10-23
"""
    assert validate_adr_meta(content) == ["- Status:", "- Date:"]


def test_validate_adr_meta_partial():
    content = """
- Status: 提案中
- day: 2025-10-23
"""
    assert validate_adr_meta(content) == ["- Date:"]


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
