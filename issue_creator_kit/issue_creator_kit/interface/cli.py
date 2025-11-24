import logging
import sys
from pathlib import Path

from issue_creator_kit.application import validation_service
from issue_creator_kit.infrastructure import file_system_service

logging.basicConfig(level=logging.INFO, format="%(message)s")


def main() -> int:
    """
    すべての対象ドキュメントを検証し、エラーがあれば報告します。
    """
    if len(sys.argv) > 1:
        # If filenames are passed, validate only those.
        target_files = [str(Path(f)) for f in sys.argv[1:]]
        logging.info(f"Validating specific files: {target_files}")
    else:
        # Otherwise, find all target files.
        project_root = str(Path(__file__).parent.parent.parent.parent)
        target_files = file_system_service.find_target_files(project_root)
        logging.info(f"Validating all target files: {target_files}")

    error_count = 0

    for file_path in target_files:
        p = Path(file_path)
        if not p.is_file():
            logging.warning(f"⚠️  File not found or not a regular file, skipping: {file_path}")
            continue

        doc_type = validation_service.get_document_type(file_path)
        if not doc_type:
            continue

        content = file_system_service.read_file_content(file_path)

        # 共通のセクション検証
        missing_sections = validation_service.validate_sections(content, doc_type)
        if missing_sections:
            error_count += 1
            logging.error(f"❌ {file_path}: Missing sections: {', '.join(missing_sections)}")

        # ドキュメントタイプ別の追加検証
        if doc_type == validation_service.DocumentType.ADR:
            if not validation_service.validate_adr_summary_format(content):
                error_count += 1
                logging.error(f"❌ {file_path}: Invalid ADR summary format.")
        elif doc_type == validation_service.DocumentType.DESIGN_DOC and not validation_service.validate_design_doc_overview(content):
            error_count += 1
            logging.error(f"❌ {file_path}: Invalid Design Doc overview format.")

    if error_count > 0:
        logging.error(f"\nFound {error_count} errors.")
        return 1

    logging.info("✅ All documents are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
