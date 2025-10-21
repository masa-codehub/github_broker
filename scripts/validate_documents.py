import sys
from pathlib import Path

from github_broker.infrastructure.document_validation.document_validator import (
    DocumentType,
    find_target_files,
    get_required_headers,
    validate_filename_prefix,
    validate_folder_structure,
    validate_sections,
)


def get_doc_type(file_path: str) -> DocumentType | None:
    path = Path(file_path)
    if "docs/adr" in str(path):
        return DocumentType.ADR
    if "docs/design-docs" in str(path):
        return DocumentType.DESIGN_DOC
    if "plans" in str(path):
        return DocumentType.PLAN
    return None


def main() -> int:
    base_path = Path(__file__).parent.parent.resolve()
    target_files = find_target_files(str(base_path))
    error_found = False

    for file_path in target_files:
        # Validate filename prefix
        if not validate_filename_prefix(file_path, str(base_path)):
            print(  # noqa: T201
                f"ERROR: {file_path} - Invalid filename prefix. Must be one of 'epic-', 'story-', 'task-'.",
                file=sys.stderr,
            )
            error_found = True

        # Validate folder structure
        if not validate_folder_structure(file_path, str(base_path)):
            print(  # noqa: T201
                f"ERROR: {file_path} - Invalid folder structure. 'story-*.md' must be in 'stories/' and 'task-*.md' must be in 'tasks/'.",
                file=sys.stderr,
            )
            error_found = True

        # Validate sections
        doc_type = get_doc_type(file_path)
        if doc_type:
            required_headers = get_required_headers(doc_type)
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            missing_headers = validate_sections(content, required_headers)
            if missing_headers:
                print(  # noqa: T201
                    f"ERROR: {file_path} - Missing required sections: {', '.join(missing_headers)}",
                    file=sys.stderr,
                )
                error_found = True

    return 1 if error_found else 0


if __name__ == "__main__":
    sys.exit(main())
