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
            query = f'repo:{repo_name} is:issue is:open no:assignee'
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
        """
        try:
            repo = self._client.get_repo(repo_name)
            issue = repo.get_issue(number=issue_id)
            issue.remove_from_labels(label)
            return True
        except GithubException as e:
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
            logging.error(f"Error creating branch {branch_name} in repo {repo_name}: {e}")
            raise