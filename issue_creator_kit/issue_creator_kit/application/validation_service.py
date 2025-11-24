import re
from pathlib import Path

from issue_creator_kit.domain.document import REQUIRED_HEADERS, DocumentType


def get_document_type(file_path: str) -> DocumentType | None:
    """ファイルパスからドキュメントタイプを判定します。"""
    p = Path(file_path)
    if "docs/adr" in str(p.parent):
        return DocumentType.ADR
    if "docs/design-docs" in str(p.parent):
        return DocumentType.DESIGN_DOC
    if "plans" in p.parts:
        return DocumentType.PLAN
    if "_in_box" in p.parts:
        return DocumentType.IN_BOX
    return None


def _extract_headers_from_content(content: str) -> list[str]:
    """Markdownコンテンツから `#`, `##`, `###` で始まるヘッダーを抽出します。"""
    headers = re.findall(r"^(#{1,3})\s+(.*)$", content, re.MULTILINE)
    return [f"{level} {title.strip()}" for level, title in headers]


def validate_sections(content: str, doc_type: DocumentType) -> list[str]:
    """ドキュメントに必要なセクションが含まれているか検証します。"""
    required_headers = REQUIRED_HEADERS.get(doc_type, [])
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


def validate_adr_summary_format(content: str) -> bool:
    """
    ADRの概要セクションのフォーマットを検証します。
    「# 概要 / Summary」の次の行が「[ADR-xxx]」で始まっている必要があります。
    """
    pattern = r"^# 概要 / Summary\s*\[ADR-\d+\]"
    return bool(re.search(pattern, content, re.MULTILINE | re.DOTALL))

def validate_design_doc_overview(content: str) -> bool:
    """
    Design Docの概要セクションのフォーマットを検証します。
    「# 概要 / Overview」の次の行が「デザインドキュメント:」で始まっている必要があります。
    """
    pattern = r"^# 概要 / Overview\n[ \t]*デザインドキュメント:"
    return bool(re.search(pattern, content, re.MULTILINE))

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
    filename_without_ext = p.stem

    is_story_ok = True
    if filename.startswith("story-"):
        # A story can be in a 'stories' dir, or in its own directory
        is_story_ok = (dirname == "stories") or (dirname == filename_without_ext)

    is_task_ok = True
    if filename.startswith("task-"):
        # A task can be in a 'tasks' dir, or inside a story's directory
        is_task_ok = (dirname == "tasks") or dirname.startswith("story-")

    return is_story_ok and is_task_ok
