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
        Retrieves all open, unassigned issues from a given repository.
        """
        try:
            repo = self._client.get_repo(repo_name)
            return repo.get_issues(state="open", assignee="none")
        except GithubException as e:
            print(f"Error fetching issues for repo {repo_name}: {e}")
            raise

    def update_issue_label(self, repo_name: str, issue_id: int, new_label: str):
        """
        Adds a label to a specific issue.
        """
        try:
            repo = self._client.get_repo(repo_name)
            issue = repo.get_issue(number=issue_id)
            issue.add_to_labels(new_label)
            return True
        except GithubException as e:
            print(f"Error updating issue #{issue_id} in repo {repo_name}: {e}")
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
