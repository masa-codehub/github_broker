import logging
import re
import sys
from enum import Enum, auto
from pathlib import Path
from types import MappingProxyType

logging.basicConfig(level=logging.INFO, format="%(message)s")


class DocumentType(Enum):
    ADR = auto()
    DESIGN_DOC = auto()
    PLAN = auto()
    IN_BOX = auto()


REQUIRED_HEADERS = MappingProxyType(
    {
        DocumentType.ADR: [
            "# 概要 / Summary",
            "- Status:",
            "- Date:",
            "## 状況 / Context",
            "## 決定 / Decision",
            "## 結果 / Consequences",
            "### メリット (Positive consequences)",
            "### デメリット (Negative consequences)",
            "## 検証基準 / Verification Criteria",
            "## 実装状況 / Implementation Status",
        ],
        DocumentType.DESIGN_DOC: [
            "# 概要 / Overview",
            "## 背景と課題 / Background",
            "## ゴール / Goals",
            "### 機能要件 / Functional Requirements",
            "### 非機能要件 / Non-Functional Requirements",
            "## 設計 / Design",
            "### ハイレベル設計 / High-Level Design",
            "### 詳細設計 / Detailed Design",
            "## 検討した代替案 / Alternatives Considered",
            "## セキュリティとプライバシー / Security & Privacy",
            "## 未解決の問題 / Open Questions & Unresolved Issues",
            "## 検証基準 / Verification Criteria",
            "## 実装状況 / Implementation Status",
        ],
        DocumentType.PLAN: [
            "## 親Issue (Parent Issue)",
            "## 子Issue (Sub-Issues)",
            "## As-is (現状)",
            "## To-be (あるべき姿)",
            "## 完了条件 (Acceptance Criteria)",
            "## 成果物 (Deliverables)",
            "## ブランチ戦略 (Branching Strategy)",
        ],
        DocumentType.IN_BOX: [],
    }
)


def find_target_files(base_path: str) -> list[str]:
    """
    ADR-012で定義された対象ファイルを探索し、絶対パスのリストを返します。
    """
    p = Path(base_path)
    files: list[Path] = []
    files.extend(p.joinpath("docs", "adr").rglob("*.md"))
    files.extend(p.joinpath("docs", "design-docs").rglob("*.md"))
    files.extend(p.joinpath("plans").rglob("*.md"))
    files.extend(p.joinpath("_in_box").rglob("*.md"))

    return sorted([str(f) for f in set(files)])


def validate_filename_prefix(file_path: str, base_path: str) -> bool:
    """
    plans配下のMarkdownファイル名が、epic-, story-, task- のいずれかの接頭辞で
    始まっていることを検証します。
    plans配下以外のファイルは常にTrueを返します。
    """
    p = Path(file_path)
    base = Path(base_path)
    try:
        relative_path = p.relative_to(base)
    except ValueError:
        return True  # Not a subpath, so ignore.

    if not str(relative_path).startswith("plans"):
        return True

    return bool(re.match(r"(?i)^(epic-|story-|task-).+\.md$", p.name))


def validate_folder_structure(file_path: str, base_path: str) -> bool:
    """
    plans配下のMarkdownファイルのフォルダ構成を検証します。
    - story-*.md という名前のファイルは、必ず stories/ サブディレクトリ内に配置されなければならない。
    - task-*.md という名前のファイルは、必ず tasks/ サブディレクトリ内に配置されなければならない。
    plans配下以外のファイルは常にTrueを返します。
    """
    p = Path(file_path)
    base = Path(base_path)
    try:
        relative_path = p.relative_to(base)
    except ValueError:
        return True  # Not a subpath, so ignore.

    if not str(relative_path).startswith("plans"):
        return True

    filename = p.name
    dirname = p.parent.name

    # "story-"で始まるファイルは親ディレクトリが"stories"である必要がある
    is_story_ok = (not filename.startswith("story-")) or (dirname == "stories")
    # "task-"で始まるファイルは親ディレクトリが"tasks"である必要がある
    is_task_ok = (not filename.startswith("task-")) or (dirname == "tasks")

    return is_story_ok and is_task_ok


def _extract_headers_from_content(content: str) -> list[str]:
    """Markdownコンテンツから `#`, `##`, `###` で始まるヘッダーを抽出します。"""
    headers = re.findall(r"^(#{1,3})\s+(.*)$", content, re.MULTILINE)
    return [f"{level} {title.strip()}" for level, title in headers]


def validate_sections(content: str, required_headers: list[str]) -> list[str]:
    """ドキュメントに必要なセクションが含まれているか検証します。"""
    if not required_headers:
        return []

    present_headers = set(_extract_headers_from_content(content))
    # Also check for headers without the # prefix for meta fields
    present_content_lines = {line.strip() for line in content.splitlines()}

    missing = []
    for header in required_headers:
        if header.startswith("#"):
            if header not in present_headers:
                missing.append(header)
        else:  # For meta fields like "- Status:"
            if not any(line.startswith(header) for line in present_content_lines):
                missing.append(header)
    return missing


def get_required_headers(doc_type: DocumentType) -> list[str]:
    """ドキュメントタイプに応じた必須ヘッダーのリストを返します。"""
    return REQUIRED_HEADERS.get(doc_type, [])


def validate_design_doc_overview(content: str) -> bool:
    """
    Design Docの概要セクションのフォーマットを検証します。
    「# 概要 / Overview」の次の行が「デザインドキュメント:」で始まっている必要があります。
    """
    pattern = r"^# 概要 / Overview\n[ \t]*デザインドキュメント:"
    return bool(re.search(pattern, content, re.MULTILINE))


def validate_adr_summary_format(content: str) -> bool:
    """
    ADRの概要セクションのフォーマットを検証します。
    「# 概要 / Summary」の次の行が「[ADR-xxx]」で始まっている必要があります。
    """
    pattern = r"^# 概要 / Summary\s*\[ADR-\d+\]"
    return bool(re.search(pattern, content, re.MULTILINE | re.DOTALL))


def get_document_type(file_path: str) -> DocumentType | None:
    """ファイルパスからドキュメントタイプを判定します。"""
    p = Path(file_path)
    if "docs/adr" in str(p.parent):
        return DocumentType.ADR
    if "docs/design-docs" in str(p.parent):
        return DocumentType.DESIGN_DOC
    if "plans" in str(p.parts):
        return DocumentType.PLAN
    if "_in_box" in str(p.parts):
        return DocumentType.IN_BOX
    return None


def main() -> int:
    """
    すべての対象ドキュメントを検証し、エラーがあれば報告します。
    """
    project_root = str(Path(__file__).parent.parent.parent.parent)
    target_files = find_target_files(project_root)
    error_count = 0

    for file_path in target_files:
        doc_type = get_document_type(file_path)
        if not doc_type:
            continue

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # 共通のセクション検証
        required_headers = get_required_headers(doc_type)
        missing_sections = validate_sections(content, required_headers)
        if missing_sections:
            error_count += 1
            logging.error(f"❌ {file_path}: Missing sections: {', '.join(missing_sections)}")

        # ドキュメントタイプ別の追加検証
        if doc_type == DocumentType.ADR:
            if not validate_adr_summary_format(content):
                error_count += 1
                logging.error(f"❌ {file_path}: Invalid ADR summary format.")
        elif doc_type == DocumentType.DESIGN_DOC and not validate_design_doc_overview(content):
            error_count += 1
            logging.error(f"❌ {file_path}: Invalid Design Doc overview format.")

    if error_count > 0:
        logging.error(f"\nFound {error_count} errors.")
        return 1

    logging.info("✅ All documents are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
