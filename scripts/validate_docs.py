import os
import sys
import re
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
    "plans": [
        "# 目的とゴール / Purpose and Goals",
        "## 実施内容 / Implementation",
        "## 検証結果 / Validation Results",
        "## 影響範囲と今後の課題 / Impact and Future Issues",
    ],
}


def validate_filename_and_folder_structure(filepath: str):
    path = Path(filepath)

    # Check if the file is under 'plans' directory (first part of the path)
    if path.parts[0] != "plans":
        return []

    errors = []
    basename = path.name

    # ファイル名のプレフィックス検証
    matched_prefix = False
    for prefix, expected_dir in FILENAME_PREFIXES.items():
        if basename.startswith(prefix):
            matched_prefix = True

            # フォルダ構造検証
            if prefix == "epic-":
                # epic-*.md は plans/ の直下のサブディレクトリにあるべき (plans/adr-XXX/epic-XXX.md)
                if len(path.parts) != 3:
                    errors.append(
                        f"File '{filepath}' with prefix '{prefix}' must be in a subdirectory directly under 'plans/' (e.g., plans/adr-XXX/)."
                    )
            elif prefix in ("story-", "task-"):
                # story-*.md は plans/*/stories/ に、 task-*.md は plans/*/tasks/ にあるべき
                # path.parent.name が 'stories' または 'tasks' であることを確認
                expected_parent_name = expected_dir.split('/')[-1] # 'stories' or 'tasks'
                if path.parent.name != expected_parent_name:
                    errors.append(
                        f"File '{filepath}' with prefix '{prefix}' must be in a '{expected_parent_name}/' subdirectory under 'plans/'."
                    )
            break

    if not matched_prefix:
        # plans 配下でプレフィックスがないファイルはエラー
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


ADR_SUMMARY_REGEX = re.compile(r"^\[ADR-\d+\]")


def validate_adr_summary_regex(filepath: str):
    errors = []
    path = Path(filepath)
    # Only validate files under docs/adr
    if not (path.parts[0] == "docs" and path.parts[1] == "adr"):
        return []

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.readlines()
    except FileNotFoundError:
        return [f"File not found: {filepath}"]

    # Find the line after "# 概要 / Summary"
    try:
        summary_index = [i for i, line in enumerate(content) if line.strip() == "# 概要 / Summary"][0]
        # Check the line immediately following the section header
        summary_line = content[summary_index + 1].strip()
    except IndexError:
        # Required sections validation will catch missing "# 概要 / Summary"
        return []

    if not ADR_SUMMARY_REGEX.match(summary_line):
        errors.append(
            f"File '{filepath}' summary line must match regex '{ADR_SUMMARY_REGEX.pattern}'. Found: '{summary_line}'"
        )
    return errors


def main():
    all_errors = []
    for target_path, sections in REQUIRED_SECTIONS.items():
        target_path_obj = Path(target_path)

        # Check if path exists and is a directory
        if not target_path_obj.exists() or not target_path_obj.is_dir():
            continue

        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".md"):
                    filepath = Path(root) / file

                    try:
                        all_errors.extend(validate_filename_and_folder_structure(str(filepath)))
                        all_errors.extend(validate_required_sections(str(filepath), sections))
                        
                        # ADR specific validation
                        if target_path == "docs/adr":
                            all_errors.extend(validate_adr_summary_regex(str(filepath)))
                            
                    except Exception as e:
                        all_errors.append(f"Internal Error validating {filepath}: {e}")

    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}", file=sys.stderr)  # noqa: T201
        sys.exit(1)
    else:
        print("Document validation successful!")  # noqa: T201
        sys.exit(0)


if __name__ == "__main__":
    main()
