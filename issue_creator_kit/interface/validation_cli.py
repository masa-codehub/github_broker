import argparse
import logging
import sys
from pathlib import Path

from ..application.exceptions import FrontmatterError
from ..application.validation_service import ValidationService
from ..domain.document import DocumentType

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def get_document_type(file_path: str) -> DocumentType | None:
    """ファイルパスからドキュメントタイプを判定します。"""
    if file_path.startswith("docs/adr/"):
        return DocumentType.ADR
    if file_path.startswith("docs/design-docs/"):
        return DocumentType.DESIGN_DOC
    if file_path.startswith("_in_box/"):
        return DocumentType.IN_BOX
    return None

def validate_document(file_path: str, service: ValidationService) -> list[str]:
    """1つのドキュメントを検証し、エラーメッセージのリストを返します。"""
    errors = []
    doc_type = get_document_type(file_path)

    if doc_type is None:
        return []

    try:
        content = Path(file_path).read_text(encoding="utf-8")

        if doc_type == DocumentType.IN_BOX:
            service.validate_frontmatter(file_path)

        elif doc_type in [DocumentType.ADR, DocumentType.DESIGN_DOC]:
            missing_sections = service.validate_sections(content, doc_type)
            if missing_sections:
                errors.append(f"Missing sections: {', '.join(missing_sections)}")
            if doc_type == DocumentType.ADR and not service.validate_adr_summary_format(content):
                errors.append("ADR summary format is invalid.")
            if doc_type == DocumentType.DESIGN_DOC and not service.validate_design_doc_overview(content):
                errors.append("Design Doc overview format is invalid.")

    except FileNotFoundError:
        errors.append(f"File not found: {file_path}")
    except FrontmatterError as e:
        errors.append(str(e))
    except Exception as e:
        errors.append(f"An unexpected error occurred: {e}")

    return errors

def main():
    """ドキュメント検証CLIのエントリーポイント"""
    parser = argparse.ArgumentParser(description="Validate document files.")
    parser.add_argument("files", nargs="+", help="List of files to validate.")
    args = parser.parse_args()

    service = ValidationService()
    error_count = 0
    for file_path in args.files:
        validation_errors = validate_document(file_path, service)
        if validation_errors:
            error_count += 1
            logger.error(f"❌ {file_path}:")
            for error in validation_errors:
                logger.error(f"   - {error}")

    if error_count > 0:
        logger.error(f"Found {error_count} validation errors.")
        sys.exit(1)

    logger.info("✅ All documents are valid.")
    sys.exit(0)

if __name__ == "__main__":
    main()
