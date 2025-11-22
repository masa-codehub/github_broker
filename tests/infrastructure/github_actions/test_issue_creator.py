from unittest.mock import Mock, patch

import pytest

from github_broker.infrastructure.github_actions.issue_creator import IssueCreator


class TestIssueCreator:

    @pytest.fixture
    def mock_github_client(self):
        client = Mock()
        client.repo = Mock()
        client.default_branch = "main"
        return client

    @pytest.fixture
    def mock_inbox_parser(self):
        return Mock()

    @pytest.fixture
    def issue_creator(self, mock_github_client, mock_inbox_parser):
        return IssueCreator(mock_github_client, mock_inbox_parser)

    @patch('github_broker.infrastructure.github_actions.issue_creator.get_pr_files')
    def test_create_issues_from_inbox_success(self, mock_get_pr_files, issue_creator, mock_github_client, mock_inbox_parser):
        # Setup mock for get_pr_files
        mock_pr_file = Mock()
        mock_pr_file.filename = "_in_box/test_issue.md"
        mock_pr_file.sha = "file_sha"
        mock_get_pr_files.return_value = [mock_pr_file]

        # Setup mock for github_client.get_file_content
        mock_github_client.get_file_content.return_value = "file content"

        # Setup mock for inbox_parser
        mock_inbox_parser.parse_issue_file.return_value = {
            "title": "Test Issue",
            "body": "Test Body",
            "labels": ["bug"],
            "assignees": ["user"]
        }

        # Setup mock for github_client.create_issue
        mock_issue = Mock()
        mock_issue.number = 123
        mock_github_client.create_issue.return_value = mock_issue

        # Run the method
        issue_creator.create_issues_from_inbox(pull_number=1)

        # Assertions
        mock_get_pr_files.assert_called_once_with(mock_github_client.repo, 1)
        mock_github_client.get_file_content.assert_called_once_with("_in_box/test_issue.md", "file_sha")
        mock_inbox_parser.parse_issue_file.assert_called_once_with("file content")
        mock_github_client.create_issue.assert_called_once_with("Test Issue", "Test Body", ["bug"], ["user"])
        mock_github_client.move_file.assert_called_once_with(
            "_in_box/test_issue.md",
            "_done_box/test_issue.md",
            "feat: Move _in_box/test_issue.md to _done_box after issue #123 creation",
            "file content"
        )

    @patch('github_broker.infrastructure.github_actions.issue_creator.get_pr_files')
    def test_create_issues_from_inbox_no_files(self, mock_get_pr_files, issue_creator):
        mock_get_pr_files.return_value = []
        issue_creator.create_issues_from_inbox(pull_number=1)
        mock_get_pr_files.assert_called_once_with(issue_creator.github_client.repo, 1)
        issue_creator.github_client.create_issue.assert_not_called()

    @patch('github_broker.infrastructure.github_actions.issue_creator.get_pr_files')
    def test_create_issues_from_inbox_failure_to_parse(self, mock_get_pr_files, issue_creator, mock_github_client, mock_inbox_parser):
        mock_pr_file = Mock()
        mock_pr_file.filename = "_in_box/bad_issue.md"
        mock_pr_file.sha = "file_sha"
        mock_get_pr_files.return_value = [mock_pr_file]

        mock_github_client.get_file_content.return_value = "invalid content"
        mock_inbox_parser.parse_issue_file.return_value = {"title": "", "body": ""} # Simulate parsing failure (e.g., no title)

        # Run the method
        issue_creator.create_issues_from_inbox(pull_number=1)

        # Assertions
        mock_github_client.get_file_content.assert_called_once_with("_in_box/bad_issue.md", "file_sha")
        mock_inbox_parser.parse_issue_file.assert_called_once_with("invalid content")
        mock_github_client.create_issue.assert_not_called()
        mock_github_client.move_file.assert_called_once()
        args, kwargs = mock_github_client.move_file.call_args
        assert args[0] == "_in_box/bad_issue.md"
        assert args[1] == "_failed_box/bad_issue.md"
        assert "due to error" in args[2]

    @patch('github_broker.infrastructure.github_actions.issue_creator.get_pr_files')
    def test_create_issues_from_inbox_issue_creation_failure(self, mock_get_pr_files, issue_creator, mock_github_client, mock_inbox_parser):
        mock_pr_file = Mock()
        mock_pr_file.filename = "_in_box/error_issue.md"
        mock_pr_file.sha = "file_sha"
        mock_get_pr_files.return_value = [mock_pr_file]

        mock_github_client.get_file_content.return_value = "file content"
        mock_inbox_parser.parse_issue_file.return_value = {"title": "Error Issue", "body": "Body"}
        mock_github_client.create_issue.side_effect = Exception("GitHub API Error")
        mock_github_client.repo.get_branch.return_value.commit.sha = "main_branch_sha"
        # Run the method
        issue_creator.create_issues_from_inbox(pull_number=1)

        # Assertions
        mock_github_client.create_issue.assert_called_once()
        mock_github_client.move_file.assert_called_once_with(
            "_in_box/error_issue.md",
            "_failed_box/error_issue.md",
            "fix: Move _in_box/error_issue.md to _failed_box due to error",
            "file content"
        )
