import re
from pathlib import Path


def find_target_files(base_path: str) -> list[str]:
    """
    ADR-012で定義された対象ファイルを探索し、絶対パスのリストを返します。
    """
    p = Path(base_path)
    files: list[Path] = []
    files.extend(p.joinpath("docs", "adr").glob("*.md"))
    files.extend(p.joinpath("docs", "design-docs").glob("*.md"))
    files.extend(p.joinpath("plans").rglob("*.md"))

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

    return bool(re.match(r"^(epic-|story-|task-).+\.md$", p.name))


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
