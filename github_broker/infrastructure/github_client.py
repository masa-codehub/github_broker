import os
from github import Github, GithubException
import logging

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
        Retrieves all open, unassigned issues from a given repository, 
        filtering out any that are already in progress.
        """
        try:
            query = f'repo:{repo_name} is:issue is:open -label:needs-review'
            logging.info(f"Searching for issues with query: {query}")
            all_issues = self._client.search_issues(query=query)
            
            logging.info(f"Found {all_issues.totalCount} issues initially from search.")

            filtered_issues = []
            for issue in all_issues:
                logging.info(f"  - Checking issue #{issue.number}: '{issue.title}' with labels: {[l.name for l in issue.labels]}")
                in_progress = False
                for label in issue.labels:
                    if label.name.startswith("in-progress:"):
                        in_progress = True
                        logging.info(f"    -> Issue #{issue.number} is in progress. Filtering out.")
                        break
                if not in_progress:
                    filtered_issues.append(issue)
            
            logging.info(f"Returning {len(filtered_issues)} issues after filtering.")
            return filtered_issues
        except GithubException as e:
            logging.error(f"Error searching issues for repo {repo_name}: {e}")
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
            logging.error(f"Error adding label to issue #{issue_id} in repo {repo_name}: {e}")
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
            logging.info(f"Successfully removed label '{label}' from issue #{issue_id}.")
            return True
        except GithubException as e:
            # If the label doesn't exist, GitHub API returns a 404.
            # This is not a critical error for us; the desired state (label is not present) is achieved.
            if e.status == 404:
                logging.warning(f"Label '{label}' not found on issue #{issue_id} during removal. Proceeding as this is not a critical error.")
                return True
            logging.error(f"Error removing label from issue #{issue_id} in repo {repo_name}: {e}")
            raise

    def create_branch(self, repo_name: str, branch_name: str, base_branch: str = "main"):
        """
        Creates a new branch from a base branch.
        """
        try:
            repo = self._client.get_repo(repo_name)
            source = repo.get_branch(base_branch)
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)
            return True
        except GithubException as e:
            # Check if the error is because the branch already exists
            if e.status == 422 and "Reference already exists" in str(e.data):
                logging.warning(f"Branch '{branch_name}' already exists in repo {repo_name}. Proceeding.")
                return True
            logging.error(f"Error creating branch {branch_name} in repo {repo_name}: {e}")
            raise

    def find_issue_by_label(self, repo_name: str, label: str):
        """
        Finds the first open issue that has a specific label.

        Args:
            repo_name (str): The name of the repository.
            label (str): The label to search for.

        Returns:
            The issue object if found, otherwise None.
        """
        try:
            query = f'repo:{repo_name} is:issue label:"{label}"'
            logging.info(f"Searching for issue with query: {query}")
            issues = self._client.search_issues(query=query)
            if issues.totalCount > 0:
                logging.info(f"Found issue #{issues[0].number} with label '{label}'.")
                return issues[0]
            return None
        except GithubException as e:
            logging.error(f"Error searching for issue with label {label} in repo {repo_name}: {e}")
            raise
