import pytest

from github_broker.infrastructure.document_validation.document_validator import (
    find_target_files,
    validate_filename_prefix,
    validate_folder_structure,
)


@pytest.fixture
def setup_test_files(tmp_path):
    # テスト用のディレクトリ構造とファイルを作成
    # docs/adr
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "docs" / "adr" / "001-test-adr.md").write_text("content")
    (tmp_path / "docs" / "adr" / "002-another-adr.md").write_text("content")
    # docs/design-docs
    (tmp_path / "docs" / "design-docs").mkdir(parents=True)
    (tmp_path / "docs" / "design-docs" / "design-doc-a.md").write_text("content")
    # plans
    (tmp_path / "plans").mkdir(parents=True)
    (tmp_path / "plans" / "epic-feature.md").write_text("content")
    (tmp_path / "plans" / "stories").mkdir()
    (tmp_path / "plans" / "stories" / "story-user-auth.md").write_text("content")
    (tmp_path / "plans" / "tasks").mkdir()
    (tmp_path / "plans" / "tasks" / "task-db-schema.md").write_text("content")
    (tmp_path / "plans" / "sub-dir").mkdir()
    (tmp_path / "plans" / "sub-dir" / "epic-sub-feature.md").write_text("content")

    # 対象外のファイル
    (tmp_path / "docs" / "adr" / "not-a-markdown.txt").write_text("content")
    (tmp_path / "other-file.md").write_text("content")

    return tmp_path


def test_find_target_files(setup_test_files):
    base_path = setup_test_files
    found_files = find_target_files(str(base_path))

    expected_files = [
        str(base_path / "docs" / "adr" / "001-test-adr.md"),
        str(base_path / "docs" / "adr" / "002-another-adr.md"),
        str(base_path / "docs" / "design-docs" / "design-doc-a.md"),
        str(base_path / "plans" / "epic-feature.md"),
        str(base_path / "plans" / "stories" / "story-user-auth.md"),
        str(base_path / "plans" / "sub-dir" / "epic-sub-feature.md"),
        str(base_path / "plans" / "tasks" / "task-db-schema.md"),
    ]

    assert sorted(found_files) == sorted(expected_files)


def test_find_target_files_no_files(tmp_path):
    # ファイルが一つもない場合
    base_path = tmp_path
    found_files = find_target_files(str(base_path))
    assert found_files == []


# validate_filename_prefix のテスト
@pytest.mark.parametrize(
    "file_path_suffix, expected",
    [
        ("plans/epic-test.md", True),
        ("plans/story-test.md", True),
        ("plans/task-test.md", True),
        ("plans/invalid-test.md", False),
        ("docs/adr/001-test.md", True),  # plans配下ではないのでTrue
    ],
)
def test_validate_filename_prefix(tmp_path, file_path_suffix, expected):
    file_path = tmp_path / file_path_suffix
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("content")
    assert validate_filename_prefix(str(file_path), str(tmp_path)) == expected


# validate_folder_structure のテスト
@pytest.mark.parametrize(
    "file_path_suffix, expected",
    [
        ("plans/stories/story-valid.md", True),
        ("plans/tasks/task-valid.md", True),
        ("plans/story-invalid.md", False),  # stories/ にない
        ("plans/tasks/story-invalid.md", False),  # stories/ にない
        ("plans/story-invalid/story-invalid.md", False),  # stories/ にない
        ("plans/task-invalid.md", False),  # tasks/ にない
        ("plans/stories/task-invalid.md", False),  # tasks/ にない
        ("plans/task-invalid/task-invalid.md", False),  # tasks/ にない
        ("plans/epic-valid.md", True),  # epic- はフォルダ制約なし
        ("docs/adr/001-test.md", True),  # plans配下ではないのでTrue
    ],
)
def test_validate_folder_structure(tmp_path, file_path_suffix, expected):
    file_path = tmp_path / file_path_suffix
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("content")
    assert validate_folder_structure(str(file_path), str(tmp_path)) == expected
