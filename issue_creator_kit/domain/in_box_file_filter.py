IN_BOX_DIRECTORY = "_in_box/"


def filter_in_box_files(file_list: list[str]) -> list[str]:
    """
    Given a list of file paths, filters and returns only those that are within the '_in_box/' directory.
    """
    return [file_path for file_path in file_list if file_path.startswith(IN_BOX_DIRECTORY)]
