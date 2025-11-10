import os
import sys
from pathlib import Path

from github_broker.infrastructure.document_validation.document_validator import (
    DocumentType,
    get_required_headers,
    validate_design_doc_overview,
    validate_sections,
)

FILENAME_PREFIXES = {
    "epic-": "plans",
    "story-": "plans/stories",
    "task-": "plans/tasks",
}


def validate_filename_and_folder_structure(filepath: str):
    path = Path(filepath)

    # Check if the file is under 'plans' directory (first part of the path)
    if "plans" not in path.parts:
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


def main():
    all_errors = []

    # 1. ADR と Design Doc のセクション検証
    for target_path_str, doc_type in [
        ("docs/adr", DocumentType.ADR),
        ("docs/design-docs", DocumentType.DESIGN_DOC),
    ]:
        required_sections = get_required_headers(doc_type)
        if not required_sections:
            continue
        target_path_obj = Path(target_path_str)
        if not target_path_obj.exists() or not target_path_obj.is_dir():
            continue
        for root, _, files in os.walk(target_path_obj):
            for file in files:
                if file.endswith(".md"):
                    filepath = Path(root) / file
                    try:
                        with open(filepath, encoding="utf-8") as f:
                            content = f.read()
                        missing_sections = validate_sections(content, required_sections)
                        if missing_sections:
                            for section in missing_sections:
                                all_errors.append(
                                    f"File '{filepath}' is missing required section: '{section}'."
                                )
                        if (
                            doc_type == DocumentType.DESIGN_DOC
                            and not validate_design_doc_overview(content)
                        ):
                            all_errors.append(
                                f"File '{filepath}' has an invalid overview section. The line after '# 概要 / Overview' must start with 'デザインドキュメント:'."
                            )
                    except Exception as e:
                        all_errors.append(f"Internal Error validating {filepath}: {e}")

    # 2. plans ディレクトリのファイル名とフォルダ構造検証
    plans_path_obj = Path("plans")
    if plans_path_obj.exists() and plans_path_obj.is_dir():
        for root, _, files in os.walk(plans_path_obj):
            for file in files:
                if file.endswith(".md"):
                    filepath = Path(root) / file
                    try:
                        all_errors.extend(validate_filename_and_folder_structure(str(filepath)))
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
