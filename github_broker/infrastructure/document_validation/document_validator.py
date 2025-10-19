import glob
import os
import re


def find_target_files(base_path: str) -> list[str]:
    """
    ADR-012で定義された対象ファイルを探索し、絶対パスのリストを返します。
    """
    target_patterns = [
        os.path.join(base_path, "docs", "adr", "*.md"),
        os.path.join(base_path, "docs", "design-docs", "*.md"),
        os.path.join(base_path, "plans", "**", "*.md"),
    ]

    found_files = []
    for pattern in target_patterns:
        found_files.extend(glob.glob(pattern, recursive=True))

    return sorted(set(found_files))


def validate_filename_prefix(file_path: str, base_path: str) -> bool:
    """
    plans配下のMarkdownファイル名が、epic-, story-, task- のいずれかの接頭辞で
    始まっていることを検証します。
    plans配下以外のファイルは常にTrueを返します。
    """
    relative_path = os.path.relpath(file_path, base_path)
    if not relative_path.startswith("plans"):
        return True

    filename = os.path.basename(file_path)
    return bool(re.match(r"^(epic-|story-|task-).+\.md$", filename))


def validate_folder_structure(file_path: str, base_path: str) -> bool:
    """
    plans配下のMarkdownファイルのフォルダ構成を検証します。
    - story-*.md という名前のファイルは、必ず stories/ サブディレクトリ内に配置されなければならない。
    - task-*.md という名前のファイルは、必ず tasks/ サブディレクトリ内に配置されなければならない。
    plans配下以外のファイルは常にTrueを返します。
    """
    relative_path = os.path.relpath(file_path, base_path)
    if not relative_path.startswith("plans"):
        return True

    filename = os.path.basename(file_path)
    dirname = os.path.dirname(relative_path)

    return not (
        (filename.startswith("story-") and not dirname.endswith("stories"))
        or (filename.startswith("task-") and not dirname.endswith("tasks"))
    )
