import pytest

from github_broker.infrastructure.document_validation.document_validator import (
    _extract_headers_from_content,
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


def test_validate_sections_valid(valid_adr_content):
    missing = validate_sections(valid_adr_content)
    assert not missing


def test_validate_sections_invalid(invalid_adr_content):
    missing = validate_sections(invalid_adr_content)
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
    assert headers == {"# Header 1", "## Header 2", "### Header 3"}


