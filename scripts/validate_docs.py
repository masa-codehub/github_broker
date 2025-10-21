import os
import sys

FILENAME_PREFIXES = {
    "epic-": "plans",
    "story-": "plans/stories",
    "task-": "plans/tasks",
}

REQUIRED_SECTIONS = {
    "docs/adr": ["# 概要", "## 決定", "## 状況", "## 結果"],
    "docs/design-docs": ["# 概要", "## ゴール", "## 設計", "## 考慮事項"],
    "plans": [
        "# 目的とゴール",
        "## 実施内容",
        "## 検証結果",
        "## 影響範囲と今後の課題",
    ],
}


def validate_filename_and_folder_structure(filepath):
    dirname = os.path.dirname(filepath)
    if not dirname.startswith("plans"):
        return []

    errors = []
    basename = os.path.basename(filepath)

    # ファイル名のプレフィックス検証
    matched_prefix = False
    for prefix, expected_dir in FILENAME_PREFIXES.items():
        if basename.startswith(prefix):
            matched_prefix = True
            # story-*.md と task-*.md のフォルダ構造検証
            if prefix in ("story-", "task-") and os.path.normpath(
                dirname
            ) != os.path.normpath(expected_dir):
                errors.append(
                    f"File '{filepath}' with prefix '{prefix}' must be in '{expected_dir}/' directory."
                )
            break

    if not matched_prefix:
        # plans 配下でプレフィックスがないファイルはエラー
        errors.append(
            f"File '{filepath}' in 'plans/' must start with one of {list(FILENAME_PREFIXES.keys())}."
        )

    return errors


def validate_required_sections(filepath, sections):
    errors = []
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    for section in sections:
        if section not in content:
            errors.append(
                f"File '{filepath}' is missing required section: '{section}'."
            )
    return errors


def main():
    all_errors = []
    for target_path, sections in REQUIRED_SECTIONS.items():
        if not os.path.isdir(target_path):
            continue
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".md"):
                    filepath = os.path.join(root, file)
                    all_errors.extend(validate_filename_and_folder_structure(filepath))
                    all_errors.extend(validate_required_sections(filepath, sections))

    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}", file=sys.stderr)  # noqa: T201
        sys.exit(1)
    else:
        print("Document validation successful!")  # noqa: T201
        sys.exit(0)


if __name__ == "__main__":
    main()
