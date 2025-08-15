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
        Retrieves all open, unassigned issues from a given repository that are not in progress.
        """
        try:
            query = f'repo:{repo_name} is:issue is:open no:assignee -label:"in-progress"'
            return self._client.search_issues(query=query)
        except GithubException as e:
            print(f"Error searching issues for repo {repo_name}: {e}")
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
            print(f"Error adding label to issue #{issue_id} in repo {repo_name}: {e}")
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
            print(f"Error removing label from issue #{issue_id} in repo {repo_name}: {e}")
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
            print(f"Error creating branch {branch_name} in repo {repo_name}: {e}")
            raise