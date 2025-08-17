import logging
import os

from github import Github, GithubException


class GitHubClient:
    """
    A client to interact with the GitHub API.
    """

    def __init__(self):
        token = os.getenv("GH_TOKEN")
        if not token:
            raise ValueError("GitHub token not found in GH_TOKEN environment variable.")
        self._client = Github(token)

    def get_open_issues(self, repo_name: str):
        """
        Retrieves all open issues that are not in-progress and do not need review.
        The query is now simple and relies on the presence/absence of state labels.
        """
        try:
            query = f'repo:{repo_name} is:issue is:open -label:"in-progress" -label:"needs-review"'
            logging.info(f"Searching for assignable issues with query: {query}")
            issues = self._client.search_issues(query=query)
            logging.info(f"Found {issues.totalCount} issues available for assignment.")
            return list(issues)
        except GithubException as e:
            logging.error(f"Error searching issues for repo {repo_name}: {e}")
            raise

    def find_issues_by_labels(self, repo_name: str, labels: list[str]):
        """
        Finds issues (open or closed) that have all the specified labels.
        This implementation fetches all issues and filters them manually to avoid search index delays.
        """
        try:
            repo = self._client.get_repo(repo_name)
            # Get all issues (open and closed)
            all_issues = repo.get_issues(state="all")

            required_labels = set(labels)

            for issue in all_issues:
                # Get the set of labels for the current issue
                issue_labels = {label.name for label in issue.labels}

                # Check if all required labels are present in the issue's labels
                if required_labels.issubset(issue_labels):
                    logging.info(
                        f"Found matching issue #{issue.number} with labels {issue_labels}."
                    )
                    return issue

            logging.info(f"No issue found with the required labels: {labels}")
            return None

        except GithubException as e:
            logging.error(f"Error finding issues by labels in repo {repo_name}: {e}")
            raise

    def add_label(self, repo_name: str, issue_id: int, label: str):
        """
        Adds a label to a specific issue.
        """
        try:
            repo = self._client.get_repo(repo_name)
            issue = repo.get_issue(number=issue_id)
            issue.add_to_labels(label)
            return True
        except GithubException as e:
            logging.error(
                f"Error adding label to issue #{issue_id} in repo {repo_name}: {e}"
            )
            raise

    def remove_label(self, repo_name: str, issue_id: int, label: str):
        """
        Removes a label from a specific issue.
        If the label does not exist on the issue, it logs a warning but does not raise an error.
        """
        try:
            repo = self._client.get_repo(repo_name)
            issue = repo.get_issue(number=issue_id)
            issue.remove_from_labels(label)
            logging.info(
                f"Successfully removed label '{label}' from issue #{issue_id}."
            )
            return True
        except GithubException as e:
            if e.status == 404:
                logging.warning(
                    f"Label '{label}' not found on issue #{issue_id} during removal. Proceeding as this is not a critical error."
                )
                return True
            logging.error(
                f"Error removing label from issue #{issue_id} in repo {repo_name}: {e}"
            )
            raise

    def create_branch(
        self, repo_name: str, branch_name: str, base_branch: str = "main"
    ):
        """
        Creates a new branch from a base branch.
        """
        try:
            repo = self._client.get_repo(repo_name)
            source = repo.get_branch(base_branch)
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)
            return True
        except GithubException as e:
            if e.status == 422 and "Reference already exists" in str(e.data):
                logging.warning(
                    f"Branch '{branch_name}' already exists in repo {repo_name}. Proceeding."
                )
                return True
            logging.error(
                f"Error creating branch {branch_name} in repo {repo_name}: {e}"
            )
            raise
