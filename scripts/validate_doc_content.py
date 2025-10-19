import re
import os

def extract_headers(markdown_content: str) -> list[str]:
    """
    Markdownコンテンツからヘッダー（##で始まる行）を抽出する。
    """
    headers = re.findall(r'^##\s*([^#].*)$', markdown_content, re.MULTILINE)
    return [header.strip() for header in headers]

def define_required_headers(doc_type: str) -> list[str]:
    """
    ドキュメントタイプごとに必須ヘッダーのリストを定義する。
    """
    if doc_type == "adr":
        return ["Status", "Context", "Decision", "Consequences"]
    elif doc_type == "design_doc":
        return ["Purpose", "Goals", "Non-Goals", "Architecture", "Components", "Data Model", "Security", "Future Considerations"]
    elif doc_type == "plan":
        return ["Purpose & Goal", "Implementation Details", "Verification", "Impact & Next Steps"]
    else:
        return []

def validate_document_headers(file_path: str, doc_type: str) -> bool:
    """
    ファイルのMarkdownコンテンツを読み込み、必須ヘッダーがすべて含まれているか検証する。
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    extracted_headers = extract_headers(content)
    required_headers = define_required_headers(doc_type)

    missing_headers = [header for header in required_headers if header not in extracted_headers]

    if missing_headers:
        print(f"Validation failed for {file_path} ({doc_type} type). Missing headers: {', '.join(missing_headers)}")
        return False
    else:
        print(f"Validation passed for {file_path} ({doc_type} type). All required headers are present.")
        return True

if __name__ == "__main__":
    # テスト用の使用例
    # 実際のファイルパスとドキュメントタイプに合わせて変更してください
    # 例:
    # adr_file = "/app/docs/adr/001-example-adr.md"
    # design_doc_file = "/app/docs/design-docs/001-example-design-doc.md"
    # plan_file = "/app/plans/example-plan.md"

    # print("\n--- ADR Validation ---")
    # validate_document_headers(adr_file, "adr")

    # print("\n--- Design Doc Validation ---")
    # validate_document_headers(design_doc_file, "design_doc")

    # print("\n--- Plan Validation ---")
    # validate_document_headers(plan_file, "plan")
    pass
