
import logging

import github
from github import Github, InputGitTreeElement

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

    def move_file(self, old_file_path: str, new_file_path: str, commit_message: str, file_content: str | None = None):
        """
        Moves a file by creating a new commit. If file_content is None, it implies deletion.
        """
        try:
            # Get the latest commit SHA of the default branch
            head_sha = self.repo.get_branch(self.default_branch).commit.sha
            base_tree = self.repo.get_git_tree(head_sha)

            elements = []

            # Add new file if content is provided
            if file_content is not None:
                new_blob = self.repo.create_git_blob(file_content, "utf-8")
                elements.append(InputGitTreeElement(path=new_file_path, mode='100644', type='blob', sha=new_blob.sha))

            # Mark old file for deletion if paths are different.
            if old_file_path and old_file_path != new_file_path:
                elements.append(InputGitTreeElement(path=old_file_path, mode='100644', type='blob', sha=None))

            if not elements: # No changes to commit
                logger.info("No file changes to commit.")
                return None

            new_tree = self.repo.create_git_tree(elements, base_tree=base_tree)
            parent = self.repo.get_git_commit(head_sha)
            new_commit = self.repo.create_git_commit(commit_message, new_tree, [parent])

            # Update the default branch reference
            self.repo.get_git_ref(f"heads/{self.default_branch}").edit(sha=new_commit.sha)
            logger.info(f"Successfully moved/updated file(s) with commit: {new_commit.sha}")
            return new_commit
        except Exception as e:
            logger.error(f"Error moving/updating file: {e}")
            raise

