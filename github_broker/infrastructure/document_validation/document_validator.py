import re

REQUIRED_SECTIONS = {
    "# 概要 / Summary",
    "- Status:",
    "- Date:",
    "## 状況 / Context",
    "## 決定 / Decision",
    "## 結果 / Consequences",
    "### メリット (Positive consequences)",
    "### デメリット (Negative consequences)",
    "## 検証基準 / Verification Criteria",
    "## 実装状況 / Implementation Status",
}


def validate_sections(content: str) -> list[str]:
    present_headers = _extract_headers_from_content(content)
    content_lines = content.splitlines()
    missing_sections = []

    for section in REQUIRED_SECTIONS:
        found = False
        if section.startswith("#"):
            if section in present_headers:
                found = True
        elif section.startswith("-"):
            for line in content_lines:
                if line.strip().startswith(section):
                    found = True
                    break
        if not found:
            missing_sections.append(section)
    return missing_sections


def _extract_headers_from_content(content: str) -> set[str]:
    """Extracts only Markdown headers (lines starting with #) from the content."""
    headers = set()
    for line in content.splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith("#"):
            headers.add(stripped_line)
    return headers


def validate_adr_summary_format(content: str) -> list[str]:
    errors = []
    lines = content.splitlines()
    summary_found = False
    for i, line in enumerate(lines):
        if line.strip() == "# 概要 / Summary":
            summary_found = True
            # Find the next non-empty line
            next_line_found = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line:
                    if not re.match(r"^\[ADR-\d+\]", next_line):
                        errors.append(
                            "ADR summary must be followed by a line in the format '[ADR-xxx]'."
                        )
                    next_line_found = True
                    break
            if not next_line_found:
                errors.append(
                    "ADR summary must be followed by a line in the format '[ADR-xxx]'."
                )
            break

    if not summary_found:
        errors.append("ADR must contain a '# 概要 / Summary' section.")

    return errors
