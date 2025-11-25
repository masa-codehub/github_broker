
import argparse
import logging
import sys
from pathlib import Path

from issue_creator_kit.application.validation_service import (
    get_document_type,
    validate_adr_summary_format,
    validate_design_doc_overview,
    validate_filename_prefix,
    validate_folder_structure,
    validate_sections,
)
from issue_creator_kit.domain.document import DocumentType

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def validate_document(file_path: str) -> list[str]:
    """1つのドキュメントを検証し、エラーメッセージのリストを返します。"""
    errors = []
    try:
        content = Path(file_path).read_text(encoding="utf-8")
        doc_type = get_document_type(file_path)

        if doc_type is None:
            return []  # サポート対象外のドキュメントはスキップ

        # セクションの検証
        missing_sections = validate_sections(content, doc_type)
        if missing_sections:
            errors.append(f"Missing sections: {', '.join(missing_sections)}")

        # ADR特有の検証
        if doc_type == DocumentType.ADR and not validate_adr_summary_format(content):
            errors.append("ADR summary format is invalid. Must start with '[ADR-xxx]' after the summary header.")

        # Design Doc特有の検証
        if doc_type == DocumentType.DESIGN_DOC and not validate_design_doc_overview(content):
            errors.append("Design Doc overview format is invalid. Must start with 'デザインドキュメント:' after the overview header.")

        # plans配下のファイル名の検証
        if not validate_filename_prefix(file_path, "."):
            errors.append("Markdown files under 'plans/' must have a prefix: epic-, story-, or task-.")

        # plans配下のフォルダ構成の検証
        if not validate_folder_structure(file_path, "."):
            errors.append("Invalid folder structure for story-* or task-* files under 'plans/'.")


    except FileNotFoundError:
        errors.append("File not found.")
    except Exception as e:
        errors.append(f"An unexpected error occurred: {e}")

    return errors

def main():
    """ドキュメント検証CLIのエントリーポイント"""
    parser = argparse.ArgumentParser(description="Validate document files.")
    parser.add_argument("files", nargs="+", help="List of files to validate.")
    args = parser.parse_args()

    error_count = 0
    for file_path in args.files:
        validation_errors = validate_document(file_path)
        if validation_errors:
            error_count += 1
            logger.error(f"❌ {file_path}:")
            for error in validation_errors:
                logger.error(f"   - {error}")

    if error_count == 0:
        logger.info("✅ All documents are valid.")
        return 0
    logger.error(f"Found {error_count} errors.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
