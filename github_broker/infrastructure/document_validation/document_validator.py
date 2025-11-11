
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


