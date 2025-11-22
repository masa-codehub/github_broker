import logging
import os

# Use the consolidated parser
from github_broker.infrastructure.document_validation.issue_parser import (
    parse_issue_content,
)
from github_broker.infrastructure.github_actions.github_action_utils import (
    get_pr_files,
    get_unique_path,
)

logger = logging.getLogger(__name__)

class IssueCreator:
    INBOX_PATH = "_in_box"
    DONE_BOX_PATH = "_done_box"
    FAILED_BOX_PATH = "_failed_box"

    # Remove inbox_parser from __init__
    def __init__(self, github_client):
        self.github_client = github_client

    def create_issues_from_inbox(self, pull_number: int):
        logger.info(f"Processing _in_box for pull request #{pull_number}")

        repo = self.github_client.repo

        pr_files = get_pr_files(repo, pull_number)
        # Use '/' instead of os.sep per review comment
        inbox_files = [f for f in pr_files if f.filename.startswith(self.INBOX_PATH + "/")]

        if not inbox_files:
            logger.info("No files found in _in_box directory for this PR.")
            return

        for pr_file in inbox_files:
            file_path = pr_file.filename
            file_content = None  # Initialize file_content
            logger.info(f"Processing file: {file_path}")

            try:
                # Get the content of the file from the PR's head
                file_content = self.github_client.get_file_content(file_path, pr_file.sha)
                if file_content is None:
                    raise ValueError(f"Could not retrieve content for file: {file_path}")

                # Use the new consolidated parser
                issue_details = parse_issue_content(file_content)
                if issue_details is None:
                    raise ValueError(f"Failed to parse issue file, title might be missing or format is invalid: {file_path}")

                # Get details from the IssueData object
                title = issue_details.title
                body = issue_details.body
                labels = issue_details.labels
                assignees = issue_details.assignees

                issue = self.github_client.create_issue(title, body, labels, assignees)

                # Move file to _done_box
                new_path = get_unique_path(self.DONE_BOX_PATH, os.path.basename(file_path))
                commit_message = f"feat: Move {file_path} to {new_path} after issue #{issue.number} creation"
                self.github_client.move_file(file_path, new_path, commit_message, file_content)

            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")

                # Per review, ensure we move the file even if content fetching failed initially.
                if file_content is None:
                    try:
                        file_content = self.github_client.get_file_content(file_path, pr_file.sha)
                        if file_content is None: # If it's still None (e.g. it was a directory)
                             file_content = "" # Move an empty file
                    except Exception as fetch_err:
                        logger.error(f"Could not re-fetch content for failed file {file_path}. Moving an empty file. Error: {fetch_err}")
                        file_content = "" # Move an empty file if re-fetch fails

                # Now file_content is guaranteed to be a string
                new_path = get_unique_path(self.FAILED_BOX_PATH, os.path.basename(file_path))
                commit_message = f"fix: Move {file_path} to {new_path} due to error"
                self.github_client.move_file(file_path, new_path, commit_message, file_content)
