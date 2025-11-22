import logging
import os

from github_broker.infrastructure.github_actions.github_action_utils import get_pr_files

logger = logging.getLogger(__name__)

class IssueCreator:
    INBOX_PATH = "_in_box"
    DONE_BOX_PATH = "_done_box"
    FAILED_BOX_PATH = "_failed_box"

    def __init__(self, github_client, inbox_parser):
        self.github_client = github_client
        self.inbox_parser = inbox_parser

    def create_issues_from_inbox(self, pull_number: int):
        logger.info(f"Processing _in_box for pull request #{pull_number}")

        repo = self.github_client.repo

        pr_files = get_pr_files(repo, pull_number)
        inbox_files = [f for f in pr_files if f.filename.startswith(self.INBOX_PATH + os.sep)]

        if not inbox_files:
            logger.info("No files found in _in_box directory for this PR.")
            return

        for pr_file in inbox_files:
            file_path = pr_file.filename
            logger.info(f"Processing file: {file_path}")

            try:
                # Get the content of the file from the PR's head
                file_content = self.github_client.get_file_content(file_path, pr_file.sha)
                if not file_content:
                    raise ValueError(f"Could not retrieve content for file: {file_path}")

                issue_details = self.inbox_parser.parse_issue_file(file_content)

                title = issue_details.get("title")
                body = issue_details.get("body")
                labels = issue_details.get("labels")
                assignees = issue_details.get("assignees")

                if not title:
                    raise ValueError(f"Issue title not found in file: {file_path}")

                issue = self.github_client.create_issue(title, body, labels, assignees)

                # Move file to _done_box
                new_path = os.path.join(self.DONE_BOX_PATH, os.path.basename(file_path))
                commit_message = f"feat: Move {file_path} to {self.DONE_BOX_PATH} after issue #{issue.number} creation"
                self.github_client.move_file(file_path, new_path, commit_message, file_content)

            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                # Move file to _failed_box
                new_path = os.path.join(self.FAILED_BOX_PATH, os.path.basename(file_path))
                commit_message = f"fix: Move {file_path} to {self.FAILED_BOX_PATH} due to error"
                # Reuse the already retrieved file_content
                self.github_client.move_file(file_path, new_path, commit_message, file_content)
