import logging
import sys
from unittest.mock import patch

from issue_creator_kit.interface.cli import main


def test_main_success(caplog, tmp_path):
    caplog.set_level(logging.INFO)

    # Create a temporary file with valid content
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    valid_file = adr_dir / "valid.md"
    valid_file.write_text("""
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
""", encoding="utf-8")

    # Patch sys.argv to simulate passing the file as a command-line argument
    with patch.object(sys, 'argv', ['-m', 'issue_creator_kit.interface.cli', str(valid_file)]):
        assert main() == 0
        assert "✅ All documents are valid." in caplog.text


def test_main_failure(caplog, tmp_path):
    caplog.set_level(logging.INFO)

    # Create a temporary file with invalid content
    invalid_content = """
# 概要 / Summary
[ADR-001]

## 状況 / Context
Some context here.
"""
    # Create subdirectory to match get_document_type logic
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    invalid_file = adr_dir / "invalid.md"
    invalid_file.write_text(invalid_content, encoding="utf-8")

    # Patch sys.argv to simulate passing the file as a command-line argument
    with patch.object(sys, 'argv', ['-m', 'issue_creator_kit.interface.cli', str(invalid_file)]):
        assert main() == 1
        assert f"❌ {str(invalid_file)}: Missing sections:" in caplog.text
        assert "Found 1 errors." in caplog.text
