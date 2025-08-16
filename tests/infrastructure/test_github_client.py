from unittest.mock import patch, MagicMock
import pytest

from github_broker.infrastructure.github_client import GitHubClient


@patch('os.getenv')
@patch('github_broker.infrastructure.github_client.Github')
def test_get_open_issues_filters_in_progress(mock_github, mock_getenv):
    """
    Test that get_open_issues filters out issues that have an 'in-progress' label.
    """
    # Arrange
    mock_getenv.return_value = "fake_token"
    
    mock_issue_in_progress = MagicMock()
    mock_issue_in_progress.number = 1
    mock_issue_in_progress.title = "In Progress Issue"
    mock_label_in_progress = MagicMock()
    mock_label_in_progress.name = "in-progress:agent-007"
    mock_issue_in_progress.labels = [mock_label_in_progress]

    mock_issue_open = MagicMock()
    mock_issue_open.number = 2
    mock_issue_open.title = "Open Issue"
    mock_issue_open.labels = []

    # Mock the PaginatedList object returned by search_issues
    mock_search_result = MagicMock()
    mock_search_result.totalCount = 2
    mock_search_result.__iter__.return_value = [mock_issue_in_progress, mock_issue_open]

    mock_github_instance = MagicMock()
    mock_github_instance.search_issues.return_value = mock_search_result
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    repo_name = "test/repo"

    # Act
    issues = client.get_open_issues(repo_name)

    # Assert
    expected_query = f'repo:{repo_name} is:issue is:open -label:needs-review'
    mock_github_instance.search_issues.assert_called_once_with(query=expected_query)
    
    assert len(issues) == 1
    assert issues[0].title == "Open Issue"


@patch('os.getenv')
@patch('github_broker.infrastructure.github_client.Github')
def test_add_label_success(mock_github, mock_getenv):
    """
    Test that add_label calls the github library with correct parameters.
    """
    # Arrange
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_repo.get_issue.return_value = mock_issue
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    repo_name = "test/repo"
    issue_id = 123
    label_to_add = "in-progress"

    # Act
    result = client.add_label(repo_name, issue_id, label_to_add)

    # Assert
    mock_github_instance.get_repo.assert_called_once_with(repo_name)
    mock_repo.get_issue.assert_called_once_with(number=issue_id)
    mock_issue.add_to_labels.assert_called_once_with(label_to_add)
    assert result is True


@patch('os.getenv')
@patch('github_broker.infrastructure.github_client.Github')
def test_remove_label_success(mock_github, mock_getenv):
    """
    Test that remove_label calls the github library with correct parameters.
    """
    # Arrange
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_repo.get_issue.return_value = mock_issue
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    repo_name = "test/repo"
    issue_id = 123
    label_to_remove = "in-progress"

    # Act
    result = client.remove_label(repo_name, issue_id, label_to_remove)

    # Assert
    mock_github_instance.get_repo.assert_called_once_with(repo_name)
    mock_repo.get_issue.assert_called_once_with(number=issue_id)
    mock_issue.remove_from_labels.assert_called_once_with(label_to_remove)
    assert result is True


@patch('os.getenv')
@patch('github_broker.infrastructure.github_client.Github')
def test_create_branch_success(mock_github, mock_getenv):
    """
    Test that create_branch calls the github library with correct parameters.
    """
    # Arrange
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_source_branch = MagicMock()
    mock_source_branch.commit.sha = "abcdef123456"
    mock_repo.get_branch.return_value = mock_source_branch
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance

    client = GitHubClient()
    repo_name = "test/repo"
    branch_name = "feature/new-thing"
    base_branch = "main"

    # Act
    result = client.create_branch(repo_name, branch_name, base_branch)

    # Assert
    mock_github_instance.get_repo.assert_called_once_with(repo_name)
    mock_repo.get_branch.assert_called_once_with(base_branch)
    mock_repo.create_git_ref.assert_called_once_with(
        ref=f"refs/heads/{branch_name}",
        sha="abcdef123456"
    )
    assert result is True


# --- Integration Tests ---
import os
import time
from github import Github, GithubException

# Marker to skip tests if environment variables are not set
requires_github_token = pytest.mark.skipif(
    not os.getenv("GH_TOKEN") or not os.getenv("GITHUB_REPOSITORY"),
    reason="GH_TOKEN and GITHUB_REPOSITORY environment variables required for integration tests"
)

@pytest.fixture(scope="module")
def github_client():
    """Provides a GitHubClient instance for integration tests."""
    return GitHubClient()

@pytest.fixture(scope="module")
def test_repo_name():
    """Provides the repository name from environment variables."""
    return os.getenv("GITHUB_REPOSITORY")

@pytest.fixture(scope="module")
def raw_github_client():
    """Provides a raw PyGithub instance for test setup and teardown."""
    token = os.getenv("GH_TOKEN")
    if not token:
        pytest.skip("GH_TOKEN is not set.")
    return Github(token)

@requires_github_token
def test_integration_lifecycle(github_client, test_repo_name, raw_github_client):
    """
    Tests the full lifecycle of issue and branch management.
    This single test combines setup, execution, and cleanup to ensure atomicity
    and prevent orphaned test data in the repository.
    """
    repo = raw_github_client.get_repo(test_repo_name)
    
    # --- Test Data ---
    unique_id = int(time.time())
    issue_to_filter_title = f"Test Issue to be Filtered - {unique_id}"
    issue_to_keep_title = f"Test Issue to be Kept - {unique_id}"
    label_in_progress = f"in-progress:test-agent-{unique_id}"
    label_to_add_remove = f"test-label-{unique_id}"
    branch_to_create = f"feature/test-branch-{unique_id}"
    
    issue_to_filter = None
    issue_to_keep = None

    try:
        # 1. --- SETUP ---
        # Create two issues for testing get_open_issues
        issue_to_filter = repo.create_issue(title=issue_to_filter_title, body="This issue should be filtered out.")
        issue_to_filter.add_to_labels(label_in_progress)
        
        issue_to_keep = repo.create_issue(title=issue_to_keep_title, body="This issue should be returned.")
        
        # Give GitHub's API a moment to process the new issues and labels
        time.sleep(5)

        # 2. --- TEST get_open_issues ---
        print(f"--- Running: TEST get_open_issues ---")
        open_issues = github_client.get_open_issues(test_repo_name)
        
        # Assert that the filtered issue is not present and the kept issue is
        issue_numbers = [issue.number for issue in open_issues]
        print(f"Found open issue numbers: {issue_numbers}")
        print(f"Expecting to find issue #{issue_to_keep.number}, and not find issue #{issue_to_filter.number}")
        
        assert issue_to_keep.number in issue_numbers
        assert issue_to_filter.number not in issue_numbers
        print("--- PASSED: TEST get_open_issues ---")

        # 3. --- TEST add_label and remove_label ---
        print(f"--- Running: TEST add_label and remove_label for issue #{issue_to_keep.number} ---")
        # Add a label
        github_client.add_label(test_repo_name, issue_to_keep.number, label_to_add_remove)
        time.sleep(2)
        issue_reloaded = repo.get_issue(issue_to_keep.number)
        assert label_to_add_remove in [label.name for label in issue_reloaded.labels]
        print(f"Successfully added label '{label_to_add_remove}'")

        # Remove the label
        github_client.remove_label(test_repo_name, issue_to_keep.number, label_to_add_remove)
        time.sleep(2)
        issue_reloaded = repo.get_issue(issue_to_keep.number)
        assert label_to_add_remove not in [label.name for label in issue_reloaded.labels]
        print(f"Successfully removed label '{label_to_add_remove}'")
        print("--- PASSED: TEST add_label and remove_label ---")

        # 4. --- TEST create_branch ---
        print(f"--- Running: TEST create_branch ---")
        github_client.create_branch(test_repo_name, branch_to_create, base_branch="main")
        time.sleep(2)
        # Verify branch exists
        try:
            repo.get_branch(branch_to_create)
            branch_exists = True
        except GithubException as e:
            if e.status == 404:
                branch_exists = False
            else:
                raise
        assert branch_exists, f"Branch '{branch_to_create}' was not created."
        print(f"Successfully created branch '{branch_to_create}'")
        print("--- PASSED: TEST create_branch ---")

    finally:
        # 5. --- CLEANUP ---
        print("--- Running: Cleanup ---")
        # Close issues
        if issue_to_filter:
            print(f"Closing issue #{issue_to_filter.number}")
            issue_to_filter.edit(state="closed")
        if issue_to_keep:
            print(f"Closing issue #{issue_to_keep.number}")
            issue_to_keep.edit(state="closed")
            
        # Delete branch
        try:
            ref = repo.get_git_ref(f"heads/{branch_to_create}")
            print(f"Deleting branch '{branch_to_create}'")
            ref.delete()
        except GithubException as e:
            if e.status != 404: # Ignore if branch doesn't exist
                print(f"Warning: Could not delete branch '{branch_to_create}': {e}")
        print("--- Cleanup Finished ---")