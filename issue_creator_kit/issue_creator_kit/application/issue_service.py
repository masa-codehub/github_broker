import logging
import os

import yaml

from issue_creator_kit.application.utils import get_unique_path
from issue_creator_kit.domain.issue import IssueData
from issue_creator_kit.infrastructure.github_service import GithubService

logger = logging.getLogger(__name__)

class IssueCreationService:
    """
    IssueCreationService is responsible for managing the creation of GitHub issues
    from files located in a pull request's `_in_box` directory. It processes each file,
    attempts to create a corresponding GitHub issue using the provided GithubService,
    and then moves the file to either the `_done_box` (on success) or `_failed_box` (on failure).

    Responsibilities:
        - Retrieve and process files from the `_in_box` directory in a PR.
        - Parse file contents to extract issue details (title, body, labels, assignees).
        - Create GitHub issues using the extracted information.
        - Move processed files to appropriate directories based on the outcome.
        - Log processing steps and errors for traceability.

    Usage:
        Instantiate with a GithubService instance, then call `create_issues_from_inbox(pull_number)`
        to process all files in the `_in_box` for the given pull request.
    """
    INBOX_PATH = "_in_box"
    DONE_BOX_PATH = "_done_box"
    FAILED_BOX_PATH = "_failed_box"

    def __init__(self, github_service: GithubService):
        self.github_service = github_service

    def _move_file_locally(self, old_path: str, new_path: str, content: str):
        """Moves a file locally within the runner's workspace."""
        try:
            # Ensure the destination directory exists
            os.makedirs(os.path.dirname(new_path), exist_ok=True)

            # Write the content to the new file
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Remove the old file
            os.remove(old_path)
            logger.info(f"Successfully moved file locally from {old_path} to {new_path}")
        except OSError as e:
            logger.error(f"Error moving file locally from {old_path} to {new_path}: {e}")
            raise

    def create_issues_from_inbox(self, pull_number: int) -> bool:
        """
        Processes files in the `_in_box` directory from the repo, creates GitHub issues,
        and moves the files locally to `_done_box` or `_failed_box`.
        """
        logger.info(f"Scanning _in_box directory after merge to pull request #{pull_number}")
        moved_files = False

        inbox_files = self.github_service.get_inbox_files_from_repo()

        if not inbox_files:
            logger.info("No files found in _in_box directory.")
            return False

        for file_obj in inbox_files:
            file_path = file_obj.path
            file_content = None  # Initialize for the error handling block
            logger.info(f"Processing file: {file_path}")

            try:
                # Directly decode content from the fetched file object
                file_content = file_obj.decoded_content.decode('utf-8')
                if file_content is None:
                    raise ValueError(f"Could not decode content for file: {file_path}")

                issue_details = parse_issue_content(file_content)
                if issue_details is None:
                    raise ValueError(f"Failed to parse issue file, title might be missing or format is invalid: {file_path}")

                self.github_service.create_issue(
                    title=issue_details.title,
                    body=issue_details.body,
                    labels=issue_details.labels,
                    assignees=issue_details.assignees
                )

                new_path = get_unique_path(self.DONE_BOX_PATH, os.path.basename(file_path))
                self._move_file_locally(file_path, new_path, file_content)
                moved_files = True

            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")

                # Ensure content is a string for the move operation, even in case of failure
                if file_content is None:
                    file_content = ""
                    logger.warning(f"File content was not available for {file_path}. Moving an empty file to {self.FAILED_BOX_PATH}.")

                new_path = get_unique_path(self.FAILED_BOX_PATH, os.path.basename(file_path))
                self._move_file_locally(file_path, new_path, file_content)
                moved_files = True

        return moved_files


def _sanitize_string_list(data: object) -> list[str]:
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, str)]


def parse_issue_content(content: str) -> IssueData | None:
    """
    ファイルコンテンツからイシューデータ（タイトル、本文、ラベル、担当者）を抽出します。

    パラメータ:
        content (str): 解析対象のファイルコンテンツ。YAML Front Matter（---で囲まれた部分）の後にMarkdown本文が続く形式である必要があります。
            例:
                ---
                title: "サンプルイシュー"
                labels: ["bug", "urgent"]
                assignees: ["user1"]
                ---
                これはイシューの本文です。

    戻り値:
        IssueData | None: 抽出されたイシューデータ（タイトル、本文、ラベル、担当者）を含むIssueDataインスタンス。
            フロントマターが無効または必須項目（title）が不足している場合はNoneを返します。

    期待されるフォーマット:
        - ファイルの先頭に'---'で囲まれたYAML Front Matterがあり、その後にMarkdown形式の本文が続くこと。
        - YAML Front Matterには少なくとも'title'キーが必要です。'labels'および'assignees'は省略可能です（省略時は空リスト）。

    例:
        >>> content = '''---
        ... title: "Sample Issue"
        ... labels: ["bug"]
        ... assignees: ["alice"]
        ... ---
        ... Issue body here.
        ... '''
        >>> data = parse_issue_content(content)
        >>> data.title
        'Sample Issue'
        >>> data.body
        'Issue body here.'
        >>> data.labels
        ['bug']
        >>> data.assignees
        ['alice']

        # フロントマターが無効な場合
        >>> invalid_content = 'No front matter here'
        >>> parse_issue_content(invalid_content) is None
        True
    """
    parts = content.split('---', 2)

    if len(parts) < 3:
        return None

    front_matter_str = parts[1].strip()
    body = parts[2].strip()

    try:
        metadata = yaml.safe_load(front_matter_str)
    except yaml.YAMLError:
        return None

    if not isinstance(metadata, dict):
        return None

    title = metadata.get('title')
    if not isinstance(title, str) or not title.strip():
        return None

    labels = _sanitize_string_list(metadata.get('labels'))
    assignees = _sanitize_string_list(metadata.get('assignees'))

    return IssueData(title=title, body=body, labels=labels, assignees=assignees)
