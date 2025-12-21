
import logging

import github
from github import Github

logger = logging.getLogger(__name__)

class GithubService:
    def __init__(self, github_token: str, repo_full_name: str):
        self.g = Github(github_token)
        self.repo = self.g.get_repo(repo_full_name)
        self.default_branch = self.repo.default_branch

    def get_pr_files(self, pull_number: int):
        """
        Retrieves the list of files changed in a given Pull Request.
        """
        pr = self.repo.get_pull(pull_number)
        return pr.get_files()

    def create_issue(self, title: str, body: str, labels: list | None = None, assignees: list | None = None):
        """
        Creates a new GitHub issue.
        """
        try:
            issue = self.repo.create_issue(title=title, body=body, labels=labels if labels is not None else [], assignees=assignees if assignees is not None else [])
            logger.info(f"Successfully created issue: {issue.html_url}")
            return issue
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            raise

    def get_file_content(self, file_path: str, ref: str):
        """
        Retrieves the content of a file from the repository.
        """
        try:
            contents = self.repo.get_contents(file_path, ref=ref)
            if isinstance(contents, list):
                # If contents is a list, it means file_path was a directory
                return None
            return contents.decoded_content.decode('utf-8')
        except github.UnknownObjectException:
            return None

    def get_inbox_files_from_repo(self, path: str = "_in_box") -> list:
        """
        Recursively retrieves all file contents from a given directory in the repository.
        """
        try:
            initial_contents = self.repo.get_contents(path, ref=self.default_branch)

            # Ensure contents is a list for uniform processing
            if not isinstance(initial_contents, list):
                contents = [initial_contents]
            else:
                contents = initial_contents

            file_list = []
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    # The result of get_contents can also be a single item or a list
                    dir_contents = self.repo.get_contents(file_content.path, ref=self.default_branch)
                    if isinstance(dir_contents, list):
                        contents.extend(dir_contents)
                    else:
                        contents.append(dir_contents)
                else:
                    file_list.append(file_content)
            return file_list
        except github.UnknownObjectException:
            logger.warning(f"Directory not found: {path}")
            return []

