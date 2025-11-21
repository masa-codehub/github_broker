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

def test_filter_in_box_files_correctly_filters():
    """
    Test that the function correctly filters _in_box/ files.
    """
    file_list = [
        "src/main.py",
        "_in_box/doc1.md",
        "docs/README.md",
        "_in_box/images/img1.png",
        "tests/test_something.py",
        "another_in_box/file.txt", # Should not be included
    ]
    expected_result = [
        "_in_box/doc1.md",
        "_in_box/images/img1.png",
    ]
    assert filter_in_box_files(file_list) == expected_result

