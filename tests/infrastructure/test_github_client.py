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
    expected_query = f'repo:{repo_name} is:issue is:open no:assignee'
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