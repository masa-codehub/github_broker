from github_broker.infrastructure.document_validation.in_box_file_filter import (
    filter_in_box_files,
)


def test_filter_in_box_files_empty_list():
    """
    Test that an empty list is returned when the input list is empty.
    """
    assert filter_in_box_files([]) == []

def test_filter_in_box_files_no_in_box_files():
    """
    Test that an empty list is returned when no _in_box/ files are present.
    """
    file_list = [
        "src/main.py",
        "docs/README.md",
        "tests/test_something.py",
    ]
    assert filter_in_box_files(file_list) == []

def test_filter_in_box_files_with_in_box_files_not_filtered_yet():
    """
    Test that the function returns an empty list even when _in_box/ files are present,
    as the implementation is currently a dummy. (Red phase)
    """
    file_list = [
        "src/main.py",
        "_in_box/doc1.md",
        "docs/README.md",
        "_in_box/images/img1.png",
        "tests/test_something.py",
    ]
    assert filter_in_box_files(file_list) == []

