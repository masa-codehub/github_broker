# github_broker/infrastructure/github_actions/github_action_utils.py

import datetime
import os

import github
from github import Github


def get_unique_path(base_path: str, file_name: str) -> str:
    """
    Generates a unique file path by appending a timestamp to the file name.

    Args:
        base_path: The base directory path.
        file_name: The original file name.

    Returns:
        A unique file path.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    name, ext = os.path.splitext(file_name)
    unique_file_name = f"{name}_{timestamp}{ext}"
    return os.path.join(base_path, unique_file_name)


def get_github_repo(repo_full_name: str, github_token: str):
    """
    Initializes and returns a GitHub repository object.
    """
    g = Github(github_token)
    return g.get_user().get_repo(repo_full_name.split('/')[-1])

def get_pr_files(repo, pull_number: int):
    """
    Retrieves the list of files changed in a given Pull Request.
    """
    pr = repo.get_pull(pull_number)
    return pr.get_files()

def get_file_content(repo, file_path: str, ref: str):
    """
    Retrieves the content of a file from the repository.
    """
    try:
        contents = repo.get_contents(file_path, ref=ref)
        if isinstance(contents, list):
            # If contents is a list, it means file_path was a directory
            return None
        return contents.decoded_content.decode('utf-8')
    except github.UnknownObjectException:
        return None


# ... (rest of imports)

def create_issue(repo, title: str, body: str, labels: list | None = None, assignees: list | None = None):
    """
    Creates a new GitHub issue.
    """
    return repo.create_issue(title=title, body=body, labels=labels if labels is not None else [], assignees=assignees if assignees is not None else [])

def create_blob_and_update_tree(repo, base_tree_sha: str, path: str, content: str, mode: str = '100644', type: str = 'blob'):
    """
    Creates a new blob and updates the tree.
    """
    blob_sha = repo.create_git_blob(content, "utf-8").sha
    element = github.InputGitTreeElement(path=path, mode=mode, type=type, sha=blob_sha)
    return repo.create_git_tree([element], base_tree=repo.get_git_tree(base_tree_sha))

def create_commit_and_update_ref(repo, parent_sha: str, tree_sha: str, message: str, branch: str):
    """
    Creates a new commit and updates the branch reference.
    """
    parent = repo.get_git_commit(parent_sha)
    commit = repo.create_git_commit(message, tree_sha, [parent])
    git_ref = repo.get_git_ref(f"heads/{branch}")
    git_ref.edit(sha=commit.sha)
    return commit

def get_default_branch(repo):
    """
    Gets the default branch name of the repository.
    """
    return repo.default_branch
