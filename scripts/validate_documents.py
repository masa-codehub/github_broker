#!/usr/bin/env python
import argparse
import sys
from pathlib import Path

from github_broker.infrastructure.document_validation.document_validator import (
    validate_adr_summary_format,
    validate_sections,
)

# Define the directories to scan
DOCS_DIR = Path("docs")
ADR_DIR = DOCS_DIR / "adr"


def validate_adr(file_path: Path) -> list[str]:
    """Validates a single ADR file."""
    content = file_path.read_text()
    errors = []
    errors.extend(validate_sections(content))
    errors.extend(validate_adr_summary_format(content))
    return errors


def main():
    """Main function to validate all documents."""
    parser = argparse.ArgumentParser(
        description="Validate documentation files.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="""Optional list of files to validate.
If not provided, all relevant documents will be validated.""",
    )
    args = parser.parse_args()

    if args.files:
        files_to_validate = [Path(f) for f in args.files]
    else:
        files_to_validate = list(ADR_DIR.glob("*.md"))

    all_errors = {}
    for file_path in files_to_validate:
        if file_path.is_dir():
            continue
        if "adr" in file_path.parts:
            errors = validate_adr(file_path)
            if errors:
                all_errors[file_path] = errors

    if all_errors:
        for file_path, errors in all_errors.items():
            sys.stdout.write(f"Validation errors in {file_path}:\n")
            for error in errors:
                sys.stdout.write(f"  - {error}\n")
        sys.exit(1)

    sys.stdout.write("All documents are valid.\n")


if __name__ == "__main__":
    main()
