
import unittest
from unittest.mock import patch, MagicMock

from github_broker.infrastructure.github_client import GitHubClient

@patch('github_broker.infrastructure.github_client.Github')
@patch('os.getenv')
class TestGitHubClient(unittest.TestCase):

    def test_get_open_issues_success(self, mock_getenv, mock_github):
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
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0].title, "Test Issue 1")

    def test_update_issue_label_success(self, mock_getenv, mock_github):
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
        self.assertTrue(result)

    def test_create_branch_success(self, mock_getenv, mock_github):
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
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
