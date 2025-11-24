from unittest.mock import Mock, patch

import pytest

from github_broker.infrastructure.github_actions.issue_creator import IssueCreator

# Import the class that will be used as a return value for the mocked parser
from issue_creator_kit.domain.issue import IssueData


class TestIssueCreator:

    @pytest.fixture
    def mock_github_client(self):
        client = Mock()
        client.repo = Mock()
        client.default_branch = "main"
        return client

    @pytest.fixture
    def issue_creator(self, mock_github_client):
        # Update fixture to not use the parser
        return IssueCreator(mock_github_client)

    # Patch the new parser function
    @patch('github_broker.infrastructure.github_actions.issue_creator.parse_issue_content')
    @patch('github_broker.infrastructure.github_actions.issue_creator.get_pr_files')
    def test_create_issues_from_inbox_success(self, mock_get_pr_files, mock_parse_issue_content, issue_creator, mock_github_client):
        # Setup mock for get_pr_files
        mock_pr_file = Mock()
        mock_pr_file.filename = "_in_box/test_issue.md"
        mock_pr_file.sha = "file_sha"
        mock_get_pr_files.return_value = [mock_pr_file]

        # Setup mock for github_client.get_file_content
        mock_github_client.get_file_content.return_value = "file content"

        # Setup mock for the new parser to return an IssueData object
        mock_parse_issue_content.return_value = IssueData(
            title="Test Issue",
            body="Test Body",
            labels=["bug"],
            assignees=["user"]
        )

        # Setup mock for github_client.create_issue
        mock_issue = Mock()
        mock_issue.number = 123
        mock_github_client.create_issue.return_value = mock_issue

        # Run the method
        issue_creator.create_issues_from_inbox(pull_number=1)

        # Assertions
        mock_get_pr_files.assert_called_once_with(mock_github_client.repo, 1)
        mock_github_client.get_file_content.assert_called_once_with("_in_box/test_issue.md", "file_sha")
        mock_parse_issue_content.assert_called_once_with("file content")
        mock_github_client.create_issue.assert_called_once_with("Test Issue", "Test Body", ["bug"], ["user"])

        mock_github_client.move_file.assert_called_once()
        args, _ = mock_github_client.move_file.call_args
        assert args[0] == "_in_box/test_issue.md"
        assert args[1].startswith("_done_box/test_issue_")
        assert args[1].endswith(".md")
        assert "feat: Move _in_box/test_issue.md to" in args[2]
        assert f"after issue #{mock_issue.number} creation" in args[2]
        assert args[3] == "file content"

    @patch('github_broker.infrastructure.github_actions.issue_creator.get_pr_files')
    def test_create_issues_from_inbox_no_files(self, mock_get_pr_files, issue_creator):
        mock_get_pr_files.return_value = []
        issue_creator.create_issues_from_inbox(pull_number=1)
        mock_get_pr_files.assert_called_once_with(issue_creator.github_client.repo, 1)
        issue_creator.github_client.create_issue.assert_not_called()

    @patch('github_broker.infrastructure.github_actions.issue_creator.parse_issue_content')
    @patch('github_broker.infrastructure.github_actions.issue_creator.get_pr_files')
    def test_create_issues_from_inbox_failure_to__parse(self, mock_get_pr_files, mock_parse_issue_content, issue_creator, mock_github_client):
        mock_pr_file = Mock()
        mock_pr_file.filename = "_in_box/bad_issue.md"
        mock_pr_file.sha = "file_sha"
        mock_get_pr_files.return_value = [mock_pr_file]

        mock_github_client.get_file_content.return_value = "invalid content"
        # The new parser returns None on failure
        mock_parse_issue_content.return_value = None

        # Run the method
        issue_creator.create_issues_from_inbox(pull_number=1)

        # Assertions
        mock_github_client.get_file_content.assert_called_once_with("_in_box/bad_issue.md", "file_sha")
        mock_parse_issue_content.assert_called_once_with("invalid content")
        mock_github_client.create_issue.assert_not_called()

        mock_github_client.move_file.assert_called_once()
        args, _ = mock_github_client.move_file.call_args
        assert args[0] == "_in_box/bad_issue.md"
        assert args[1].startswith("_failed_box/bad_issue_")
        assert args[1].endswith(".md")
        assert "fix: Move _in_box/bad_issue.md to" in args[2]
        assert "due to error" in args[2]

    @patch('github_broker.infrastructure.github_actions.issue_creator.parse_issue_content')
    @patch('github_broker.infrastructure.github_actions.issue_creator.get_pr_files')
    def test_create_issues_from_inbox_issue_creation_failure(self, mock_get_pr_files, mock_parse_issue_content, issue_creator, mock_github_client):
        mock_pr_file = Mock()
        mock_pr_file.filename = "_in_box/error_issue.md"
        mock_pr_file.sha = "file_sha"
        mock_get_pr_files.return_value = [mock_pr_file]

        mock_github_client.get_file_content.return_value = "file content"
        mock_parse_issue_content.return_value = IssueData(title="Error Issue", body="Body")
        mock_github_client.create_issue.side_effect = Exception("GitHub API Error")

        # Run the method
        issue_creator.create_issues_from_inbox(pull_number=1)

        # Assertions
        mock_github_client.create_issue.assert_called_once()

        mock_github_client.move_file.assert_called_once()
        args, _ = mock_github_client.move_file.call_args
        assert args[0] == "_in_box/error_issue.md"
        assert args[1].startswith("_failed_box/error_issue_")
        assert args[1].endswith(".md")
        assert "fix: Move _in_box/error_issue.md to" in args[2]
        assert "due to error" in args[2]
        assert args[3] == "file content"
