import re
from pathlib import Path

import pytest

# Import the functions to be tested
from scripts.validate_docs import (
    ADR_SUMMARY_REGEX,
    REQUIRED_SECTIONS,
    validate_adr_summary_regex,
    validate_required_sections,
)

# --- Fixtures and Helpers ---

# Get the required sections for ADR from the script
ADR_REQUIRED_SECTIONS = REQUIRED_SECTIONS["docs/adr"]

def create_dummy_adr(tmp_path: Path, content: str, filename: str = "001-test-adr.md") -> Path:
    """Creates a dummy ADR file in a mock docs/adr structure."""
    # Mock the structure that validate_docs.py expects
    (tmp_path / "docs" / "adr").mkdir(parents=True, exist_ok=True)
    filepath = tmp_path / "docs" / "adr" / filename
    filepath.write_text(content, encoding="utf-8")
    return filepath

# --- Test Cases for ADR Required Sections ---

@pytest.mark.parametrize("missing_section", ADR_REQUIRED_SECTIONS)
def test_adr_required_sections_validation_failure(tmp_path, missing_section):
    """Tests that validation fails if any single required section is missing."""
    all_sections = set(ADR_REQUIRED_SECTIONS)

    # Construct the content by joining all sections EXCEPT the missing one.
    content_lines = []
    for section in all_sections:
        if section != missing_section:
            content_lines.append(section)

            # Add a valid summary line immediately after the summary header, if it's present
            if section == "# 概要 / Summary":
                content_lines.append("[ADR-001] Test Summary")

    content = "\n".join(content_lines)

    filepath = create_dummy_adr(tmp_path, content)

    errors = validate_required_sections(str(filepath), ADR_REQUIRED_SECTIONS)

    assert len(errors) == 1
    assert f"File '{filepath}' is missing required section: '{missing_section}'." in errors[0]

def test_adr_required_sections_validation_success(tmp_path):
    """Tests that validation succeeds when all required sections are present."""
    # Construct content with all required sections
    content_lines = []
    for section in ADR_REQUIRED_SECTIONS:
        content_lines.append(section)
        if section == "# 概要 / Summary":
            content_lines.append("[ADR-001] Test Summary")

    content = "\n".join(content_lines)

    filepath = create_dummy_adr(tmp_path, content)

    errors = validate_required_sections(str(filepath), ADR_REQUIRED_SECTIONS)

    assert errors == []

# --- Test Cases for ADR Summary Regex ---

def test_adr_summary_regex_validation_success(tmp_path):
    """Tests that validation succeeds when the summary line matches the required regex."""
    valid_summaries = [
        "[ADR-001] Initial Architecture Decision",
        "[ADR-123] Another Decision Record",
        "[ADR-001]", # Exact match
    ]

    for summary in valid_summaries:
        content = f"# 概要 / Summary\n{summary}\n\n" + "\n".join(ADR_REQUIRED_SECTIONS)
        filepath = create_dummy_adr(tmp_path, content, filename=f"001-{summary.replace(' ', '-')}.md")

        errors = validate_adr_summary_regex(str(filepath))
        assert errors == [], f"Validation failed for valid summary: {summary}"

    # Test case for blank line between header and content
    summary_with_blank_line = "[ADR-999] Test with blank line"
    content = f"# 概要 / Summary\n\n{summary_with_blank_line}\n\n" + "\n".join(ADR_REQUIRED_SECTIONS)
    filepath = create_dummy_adr(tmp_path, content, filename="999-test-blank.md")
    errors = validate_adr_summary_regex(str(filepath))
    assert errors == [], "Validation failed for valid summary with blank line after header"

@pytest.mark.parametrize("invalid_summary", [
    "ADR-001] Missing bracket",
    "[ADR-001 Missing closing bracket",
    "ADR-001 Test Summary",
    "[ADR-A01] Invalid number format",
])
def test_adr_summary_regex_validation_failure(tmp_path, invalid_summary):
    """Tests that validation fails when the summary line does not match the required regex."""
    # The regex only checks the start of the line, so we need to ensure the line is exactly what we expect
    content = f"# 概要 / Summary\n{invalid_summary}\n\n" + "\n".join(ADR_REQUIRED_SECTIONS)

    # Sanitize filename for OS compatibility
    sanitized_filename = re.sub(r'[\\\/\:\*\?\"\<\>\|]', '-', invalid_summary)[:50] + ".md"
    filepath = create_dummy_adr(tmp_path, content, filename=sanitized_filename)

    errors = validate_adr_summary_regex(str(filepath))

    assert len(errors) == 1
    assert f"File '{filepath}' summary line must match regex '{ADR_SUMMARY_REGEX.pattern}'." in errors[0]
