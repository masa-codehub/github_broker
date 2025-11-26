
import datetime
import os


def get_unique_path(base_path: str, file_name: str) -> str:
    """
    Generates a unique file path by appending a timestamp to the file name.

    Args:
        base_path: The base directory path.
        file_name: The original file name.

    Returns:
        A unique file path.
    """
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S%f")
    name, ext = os.path.splitext(file_name)
    unique_file_name = f"{name}_{timestamp}{ext}"
    return os.path.join(base_path, unique_file_name)
