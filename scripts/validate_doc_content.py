import argparse
import re
import sys


def extract_headers(markdown_content: str) -> list[str]:
    """
    Markdownコンテンツからヘッダー（##で始まる行）を抽出する。
    """
    headers = re.findall(r"^##\s*([^#].*)$", markdown_content, re.MULTILINE)
    return [header.strip() for header in headers]


def define_required_headers(doc_type: str) -> list[str]:
    """
    ドキュメントタイプごとに必須ヘッダーのリストを定義する。
    """
    required_headers_map = {
        "adr": ["Status", "Context", "Decision", "Consequences"],
        "design_doc": [
            "Purpose",
            "Goals",
            "Non-Goals",
            "Architecture",
            "Components",
            "Data Model",
            "Security",
            "Future Considerations",
        ],
        "plan": [
            "Purpose & Goal",
            "Implementation Details",
            "Verification",
            "Impact & Next Steps",
        ],
    }
    return required_headers_map.get(doc_type, [])


def validate_document_headers(file_path: str, doc_type: str) -> list[str]:
    """
    ファイルのMarkdownコンテンツを読み込み、必須ヘッダーがすべて含まれているか検証する。
    見つからないヘッダーのリストを返す。
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    extracted_headers = extract_headers(content)
    required_headers = define_required_headers(doc_type)

    return [header for header in required_headers if header not in extracted_headers]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate headers of a given markdown document."
    )
    parser.add_argument("file_path", help="Path to the markdown file.")
    parser.add_argument(
        "doc_type",
        choices=["adr", "design_doc", "plan"],
        help="Type of the document.",
    )
    args = parser.parse_args()

    try:
        missing = validate_document_headers(args.file_path, args.doc_type)
        if missing:
            print(  # noqa: T201
                f"Validation failed for {args.file_path} ({args.doc_type} type). Missing headers: {', '.join(missing)}",
                file=sys.stderr,
            )
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found at {args.file_path}", file=sys.stderr)  # noqa: T201
        sys.exit(1)
