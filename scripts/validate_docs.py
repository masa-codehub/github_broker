import argparse
import sys
from pathlib import Path

from github_broker.infrastructure.document_validation.document_validator import (
    DocumentType,
    find_target_files,
    get_required_headers,
    validate_adr_meta,
    validate_adr_summary_format,
    validate_design_doc_overview,
    validate_filename_prefix,
    validate_folder_structure,
    validate_sections,
)


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
        files_to_validate = [Path(f) for f in find_target_files(".")]

    all_errors = []

    for filepath in files_to_validate:
        try:
            # 1. plans ディレクトリのファイル名とフォルダ構造検証
            if "plans" in str(filepath):
                if not validate_filename_prefix(str(filepath), "."):
                    all_errors.append(f"File '{filepath}' has an invalid filename prefix.")
                if not validate_folder_structure(str(filepath), "."):
                    all_errors.append(f"File '{filepath}' has an invalid folder structure.")

            # 2. ADR と Design Doc のセクション検証
            doc_type = None
            if "docs/adr" in str(filepath):
                doc_type = DocumentType.ADR
            elif "docs/design-docs" in str(filepath):
                doc_type = DocumentType.DESIGN_DOC

            if doc_type:
                required_sections = get_required_headers(doc_type)
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                missing_sections = validate_sections(content, required_sections)
                if missing_sections:
                    for section in missing_sections:
                        all_errors.append(
                            f"File '{filepath}' is missing required section: '{section}'."
                        )

                if doc_type == DocumentType.ADR:
                    missing_meta = validate_adr_meta(content)
                    if missing_meta:
                        for meta in missing_meta:
                            all_errors.append(
                                f"File '{filepath}' is missing required meta field: '{meta}'."
                            )
                    if not validate_adr_summary_format(content):
                        all_errors.append(
                            f"File '{filepath}' has an invalid summary format. The line after '# 概要 / Summary' must start with '[ADR-xxx]'."
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

    if all_errors:
        for error in all_errors:
            sys.stderr.write(f"ERROR: {error}\n")
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
