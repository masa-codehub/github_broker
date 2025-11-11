import os
import re
import sys
from pathlib import Path

FILENAME_PREFIXES = {
    "epic-": "plans",
    "story-": "plans/stories",
    "task-": "plans/tasks",
}

REQUIRED_SECTIONS = {
    "docs/adr": [
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
    ],
    "docs/design-docs": [
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
    ],
}

ADR_SUMMARY_REGEX = re.compile(r"^\[ADR-\d+]")
DESIGN_DOC_OVERVIEW_REGEX = re.compile(r"^デザインドキュメント:.+")


def validate_filename_and_folder_structure(filepath: str):
    path = Path(filepath)
    if "plans" not in path.parts:
        return []

    errors = []
    basename = path.name
    matched_prefix = False
    for prefix, expected_dir in FILENAME_PREFIXES.items():
        if basename.startswith(prefix):
            matched_prefix = True
            if prefix == "epic-":
                if len(path.parts) < 3 or path.parts[-3] != "plans":
                    errors.append(
                        f"File '{filepath}' with prefix '{prefix}' must be in a subdirectory directly under 'plans/' (e.g., plans/some-epic-name/)."
                    )
            elif prefix in ("story-", "task-"):
                expected_parent_name = expected_dir.split("/")[-1]
                if path.parent.name != expected_parent_name:
                    errors.append(
                        f"File '{filepath}' with prefix '{prefix}' must be in a '{expected_parent_name}/' subdirectory."
                    )
            break

    if not matched_prefix:
        errors.append(
            f"File '{filepath}' in 'plans/' must start with one of {list(FILENAME_PREFIXES.keys())}."
        )
    return errors


def validate_required_sections(filepath: str, sections: list[str]):
    errors = []
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return [f"File not found: {filepath}"]

    for section in sections:
        if section not in content:
            errors.append(
                f"File '{filepath}' is missing required section: '{section}'."
            )
    return errors


def validate_adr_summary_regex(filepath: str):
    errors = []
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.readlines()
    except FileNotFoundError:
        return [f"File not found: {filepath}"]

    try:
        summary_index = [i for i, line in enumerate(content) if line.strip() == "# 概要 / Summary"][0]
        summary_line = ""
        for line in content[summary_index + 1:]:
            stripped_line = line.strip()
            if stripped_line:
                summary_line = stripped_line
                break
        if not summary_line:
            errors.append(f"File '{filepath}' has no summary content after '# 概要 / Summary' header.")
            return errors
    except IndexError:
        return []

    if not ADR_SUMMARY_REGEX.match(summary_line):
        errors.append(
            f"File '{filepath}' summary line must match regex '{ADR_SUMMARY_REGEX.pattern}'. Found: '{summary_line}'"
        )
    return errors


def validate_design_doc_overview(filepath: str):
    """
    Validates that the line after '# 概要 / Overview' in a Design Doc
    starts with 'デザインドキュメント:'.
    """
    errors = []
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.readlines()
    except FileNotFoundError:
        return [f"File not found: {filepath}"]

    try:
        overview_index = [i for i, line in enumerate(content) if line.strip() == "# 概要 / Overview"][0]
        overview_line = ""
        for line in content[overview_index + 1:]:
            stripped_line = line.strip()
            if stripped_line:
                overview_line = stripped_line
                break
        if not overview_line:
            errors.append(f"File '{filepath}' has no overview content after '# 概要 / Overview' header.")
            return errors
    except IndexError:
        return []

    if not DESIGN_DOC_OVERVIEW_REGEX.match(overview_line):
        errors.append(
            f"File '{filepath}' overview line must match regex '{DESIGN_DOC_OVERVIEW_REGEX.pattern}'. Found: '{overview_line}'"
        )
    return errors


def get_files_to_validate(files_from_args):
    if files_from_args:
        return [f for f in files_from_args if f.endswith(".md")]
    all_files = []
    for path in ["docs/adr", "docs/design-docs", "plans"]:
        target_path_obj = Path(path)
        if target_path_obj.exists() and target_path_obj.is_dir():
            for root, _, files in os.walk(target_path_obj):
                for file in files:
                    if file.endswith(".md"):
                        all_files.append(str(Path(root) / file))
    return all_files

def main():
    all_errors = []
    files_to_validate = get_files_to_validate(sys.argv[1:])

    for filepath in files_to_validate:
        try:
            path_obj = Path(filepath)
            # 'plans' validation
            if "plans" in path_obj.parts:
                all_errors.extend(validate_filename_and_folder_structure(filepath))

            # ADR and Design Doc validation
            for doc_type_path, sections in REQUIRED_SECTIONS.items():
                if filepath.startswith(doc_type_path):
                    all_errors.extend(validate_required_sections(filepath, sections))
                    if doc_type_path == "docs/adr":
                        all_errors.extend(validate_adr_summary_regex(filepath))
                    elif doc_type_path == "docs/design-docs":
                        all_errors.extend(validate_design_doc_overview(filepath))

        except Exception as e:
            all_errors.append(f"Internal Error validating {filepath}: {e}")

    if all_errors:
        for error in all_errors:
            sys.stderr.write(f"ERROR: {error}\n")
        sys.exit(1)
    else:
        sys.stdout.write("Document validation successful!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
