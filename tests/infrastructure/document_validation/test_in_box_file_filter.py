import pytest

from github_broker.infrastructure.document_validation.in_box_file_filter import (
    filter_in_box_files,
)


@pytest.mark.parametrize(
    ("file_list", "expected"),
    [
        ([], []),
        (
            [
                "src/main.py",
                "docs/README.md",
                "tests/test_something.py",
            ],
            [],
        ),
        (
            [
                "src/main.py",
                "_in_box/doc1.md",
                "docs/README.md",
                "_in_box/images/img1.png",
                "tests/test_something.py",
                "another_in_box/file.txt",
            ],
            ["_in_box/doc1.md", "_in_box/images/img1.png"],
        ),
    ],
    ids=["empty_list", "no_in_box_files", "correctly_filters"],
)
def test_filter_in_box_files(file_list: list[str], expected: list[str]):
    """
    Test that filter_in_box_files correctly filters files based on the '_in_box/' prefix
    across various scenarios.
    """
    assert filter_in_box_files(file_list) == expected

