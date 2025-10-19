import pytest
import os
from scripts.validate_doc_content import extract_headers, define_required_headers, validate_document_headers

# テスト用のダミーファイルパス
def create_dummy_markdown_file(tmp_path, filename, content):
    file_path = tmp_path / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return str(file_path)

def test_extract_headers():
    content = """
# Title

## Header 1
Some text.

### Sub Header

## Header 2
More text.
"""
    headers = extract_headers(content)
    assert headers == ["Header 1", "Header 2"]

    content_no_headers = """
# Title
Some text.
"""
    headers_no_headers = extract_headers(content_no_headers)
    assert headers_no_headers == []

def test_define_required_headers():
    assert define_required_headers("adr") == ["Status", "Context", "Decision", "Consequences"]
    assert define_required_headers("design_doc") == ["Purpose", "Goals", "Non-Goals", "Architecture", "Components", "Data Model", "Security", "Future Considerations"]
    assert define_required_headers("plan") == ["Purpose & Goal", "Implementation Details", "Verification", "Impact & Next Steps"]
    assert define_required_headers("unknown_type") == []

def test_validate_document_headers_success(tmp_path):
    # ADRの成功ケース
    adr_content = """
# ADR Title

## Status
Accepted

## Context
Some context.

## Decision
Decision made.

## Consequences
Consequences described.
"""
    adr_file = create_dummy_markdown_file(tmp_path, "test_adr.md", adr_content)
    assert validate_document_headers(adr_file, "adr") is True

    # Design Docの成功ケース
    design_doc_content = """
# Design Doc Title

## Purpose
Purpose of the design.

## Goals
Goals listed.

## Non-Goals
Non-goals listed.

## Architecture
Architecture overview.

## Components
Components described.

## Data Model
Data model details.

## Security
Security considerations.

## Future Considerations
Future considerations.
"""
    design_doc_file = create_dummy_markdown_file(tmp_path, "test_design_doc.md", design_doc_content)
    assert validate_document_headers(design_doc_file, "design_doc") is True

    # Planの成功ケース
    plan_content = """
# Plan Title

## Purpose & Goal
Purpose and goal.

## Implementation Details
Implementation details.

## Verification
Verification steps.

## Impact & Next Steps
Impact and next steps.
"""
    plan_file = create_dummy_markdown_file(tmp_path, "test_plan.md", plan_content)
    assert validate_document_headers(plan_file, "plan") is True

def test_validate_document_headers_failure_missing_headers(tmp_path):
    # ADRの失敗ケース (Statusが欠けている)
    adr_content_missing = """
# ADR Title

## Context
Some context.

## Decision
Decision made.

## Consequences
Consequences described.
"""
    adr_file_missing = create_dummy_markdown_file(tmp_path, "test_adr_missing.md", adr_content_missing)
    assert validate_document_headers(adr_file_missing, "adr") is False

    # Design Docの失敗ケース (Purposeが欠けている)
    design_doc_content_missing = """
# Design Doc Title

## Goals
Goals listed.

## Non-Goals
Non-goals listed.

## Architecture
Architecture overview.

## Components
Components described.

## Data Model
Data model details.

## Security
Security considerations.

## Future Considerations
Future considerations.
"""
    design_doc_file_missing = create_dummy_markdown_file(tmp_path, "test_design_doc_missing.md", design_doc_content_missing)
    assert validate_document_headers(design_doc_file_missing, "design_doc") is False

    # Planの失敗ケース (Purpose & Goalが欠けている)
    plan_content_missing = """
# Plan Title

## Implementation Details
Implementation details.

## Verification
Verification steps.

## Impact & Next Steps
Impact and next steps.
"""
    plan_file_missing = create_dummy_markdown_file(tmp_path, "test_plan_missing.md", plan_content_missing)
    assert validate_document_headers(plan_file_missing, "plan") is False

def test_validate_document_headers_file_not_found(tmp_path):
    # 存在しないファイルに対するテスト
    non_existent_file = tmp_path / "non_existent.md"
    assert validate_document_headers(str(non_existent_file), "adr") is False
