import os
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
        "## 決定 / Decision",
        "## 状況 / Context",
        "## 結果 / Consequences",
    ],
    "docs/design-docs": [
        "# 概要 / Overview",
        "## ゴール / Goals",
        "## 設計 / Design",
        "## 考慮事項 / Considerations",
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
