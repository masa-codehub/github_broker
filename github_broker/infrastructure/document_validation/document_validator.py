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
    missing_sections = []
    for section in REQUIRED_SECTIONS:
        if section not in content:
            missing_sections.append(section)
    return missing_sections


def _extract_headers_from_content(content: str) -> set[str]:
    headers = set()
    for line in content.splitlines():
        if line.startswith("#"):
            headers.add(line.strip())
    return headers


def validate_adr_summary_format(content: str) -> list[str]:
    errors = []
    lines = content.splitlines()
    summary_found = False
    for i, line in enumerate(lines):
        if line.strip() == "# 概要 / Summary":
            summary_found = True
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if not re.match(r"^\[ADR-\d+\]", next_line):
                    errors.append(
                        "ADR summary must be followed by a line in the format '[ADR-xxx]'."
                    )
            else:
                errors.append(
                    "ADR summary must be followed by a line in the format '[ADR-xxx]'."
                )
            break

    if not summary_found:
        errors.append("ADR must contain a '# 概要 / Summary' section.")

    return errors
