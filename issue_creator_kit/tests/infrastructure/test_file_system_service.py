from pathlib import Path

from issue_creator_kit.infrastructure.file_system_service import (
    find_target_files,
    read_file_content,
)


def test_find_target_files(tmp_path: Path):
    """
    Test that find_target_files correctly finds all markdown files in the specified directories.
    """
    # Create some dummy files and directories
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "docs" / "adr" / "001.md").touch()
    (tmp_path / "docs" / "design-docs").mkdir(parents=True)
    (tmp_path / "docs" / "design-docs" / "001.md").touch()
    (tmp_path / "plans").mkdir()
    (tmp_path / "plans" / "epic-1.md").touch()
    (tmp_path / "_in_box").mkdir()
    (tmp_path / "_in_box" / "task-1.md").touch()
    (tmp_path / "other").mkdir()
    (tmp_path / "other" / "other.md").touch()

    files = find_target_files(str(tmp_path))
    assert len(files) == 4
    assert str(tmp_path / "docs" / "adr" / "001.md") in files
    assert str(tmp_path / "docs" / "design-docs" / "001.md") in files
    assert str(tmp_path / "plans" / "epic-1.md") in files
    assert str(tmp_path / "_in_box" / "task-1.md") in files


def test_read_file_content(tmp_path: Path):
    """
    Test that read_file_content correctly reads the content of a file.
    """
    file_path = tmp_path / "test.txt"
    expected_content = "Hello, world!"
    file_path.write_text(expected_content, encoding="utf-8")

    content = read_file_content(str(file_path))
    assert content == expected_content
