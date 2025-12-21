from pathlib import Path


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


def read_file_content(file_path: str) -> str:
    """
    Reads and returns the content of a specified file.
    """
    with open(file_path, encoding="utf-8") as f:
        return f.read()
