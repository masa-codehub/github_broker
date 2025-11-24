import logging
import os

import yaml

from issue_creator_kit.application.utils import get_unique_path
from issue_creator_kit.domain.issue import IssueData
from issue_creator_kit.infrastructure.github_service import GithubService

logger = logging.getLogger(__name__)

class IssueCreationService:
    INBOX_PATH = "_in_box"
    DONE_BOX_PATH = "_done_box"
    FAILED_BOX_PATH = "_failed_box"

    def __init__(self, github_service: GithubService):
        self.github_service = github_service

    def create_issues_from_inbox(self, pull_number: int):
        logger.info(f"Processing _in_box for pull request #{pull_number}")

        pr_files = self.github_service.get_pr_files(pull_number)
        inbox_files = [f for f in pr_files if f.filename.startswith(self.INBOX_PATH + "/")]

        if not inbox_files:
            logger.info("No files found in _in_box directory for this PR.")
            return

        for pr_file in inbox_files:
            file_path = pr_file.filename
            file_content = None
            logger.info(f"Processing file: {file_path}")

            try:
                file_content = self.github_service.get_file_content(file_path, pr_file.sha)
                if file_content is None:
                    raise ValueError(f"Could not retrieve content for file: {file_path}")

                issue_details = parse_issue_content(file_content)
                if issue_details is None:
                    raise ValueError(f"Failed to parse issue file, title might be missing or format is invalid: {file_path}")

                issue = self.github_service.create_issue(
                    title=issue_details.title,
                    body=issue_details.body,
                    labels=issue_details.labels,
                    assignees=issue_details.assignees
                )

                new_path = get_unique_path(self.DONE_BOX_PATH, os.path.basename(file_path))
                commit_message = f"feat: Move {file_path} to {new_path} after issue #{issue.number} creation"
                self.github_service.move_file(file_path, new_path, commit_message, file_content)

            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")

                if file_content is None:
                    try:
                        file_content = self.github_service.get_file_content(file_path, pr_file.sha)
                        if file_content is None:
                             file_content = ""
                    except Exception as fetch_err:
                        logger.error(f"Could not re-fetch content for failed file {file_path}. Moving an empty file. Error: {fetch_err}")
                        file_content = ""

                new_path = get_unique_path(self.FAILED_BOX_PATH, os.path.basename(file_path))
                commit_message = f"fix: Move {file_path} to {new_path} due to error"
                self.github_service.move_file(file_path, new_path, commit_message, file_content)


def _sanitize_string_list(data: object) -> list[str]:
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, str)]


def parse_issue_content(content: str) -> IssueData | None:
    """
    ファイルコンテンツからイシューデータ（タイトル、本文、ラベル、担当者）を抽出します。
    ...
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
