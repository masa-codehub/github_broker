
import argparse
import logging
import sys

from issue_creator_kit.application.exceptions import ValidationError
from issue_creator_kit.application.validation_service import validate_frontmatter

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def validate_document(file_path: str) -> list[str]:
    """1つのドキュメントを検証し、エラーメッセージのリストを返します。"""
    errors = []
    try:
        validate_frontmatter(file_path) # 私が作成した関数を呼び出す
    except FileNotFoundError:
        errors.append(f"File not found: {file_path}")
    except ValidationError as e: # カスタム例外をキャッチ
        errors.append(str(e))
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
