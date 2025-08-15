
from unittest.mock import patch, MagicMock

from github_broker.infrastructure.github_client import GitHubClient

# @patchデコレータはpytestでもそのまま動作します。
# 下から上に適用されるため、テスト関数の引数の順番は(mock_github, mock_getenv)ではなく
# (mock_getenv, mock_github) となります。
@patch('os.getenv')
@patch('github_broker.infrastructure.github_client.Github')
def test_get_open_issues_success(mock_github, mock_getenv):
    """
    Test that get_open_issues calls the github library with correct parameters
    and returns a list of issues.
    """
    # Arrange
    mock_getenv.return_value = "fake_token"
    mock_repo = MagicMock()
    mock_issue1 = MagicMock()
    mock_issue1.title = "Test Issue 1"
    mock_issue2 = MagicMock()
    mock_issue2.title = "Test Issue 2"
    mock_repo.get_issues.return_value = [mock_issue1, mock_issue2]
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github.return_value = mock_github_instance
    
    client = GitHubClient()
    repo_name = "test/repo"

    # Act
    issues = client.get_open_issues(repo_name)

    # Assert
    mock_github_instance.get_repo.assert_called_once_with(repo_name)
    mock_repo.get_issues.assert_called_once_with(state="open", assignee="none")
    assert len(issues) == 2
    assert issues[0].title == "Test Issue 1"

@patch('os.getenv')
@patch('github_broker.infrastructure.github_client.Github')
def test_update_issue_label_success(mock_github, mock_getenv):
    """
    Test that update_issue_label calls the github library with correct parameters.
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
    new_label = "needs-review"

    # Act
    result = client.update_issue_label(repo_name, issue_id, new_label)

    # Assert
    mock_github_instance.get_repo.assert_called_once_with(repo_name)
    mock_repo.get_issue.assert_called_once_with(number=issue_id)
    mock_issue.add_to_labels.assert_called_once_with(new_label)
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
