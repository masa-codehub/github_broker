from unittest.mock import Mock

import pytest

from issue_creator_kit.application.issue_service import (
    IssueCreationService,
    parse_issue_content,
)


# Existing tests for parse_issue_content
def test_parse_issue_content_with_valid_front_matter():
    """
    Test that parse_issue_content correctly parses valid YAML Front Matter.
    """
    content = """
---
title: "Test Issue Title"
labels: ["bug", "documentation"]
assignees: ["octocat", "monalisa"]
---
This is the body of the test issue.
It can span multiple lines.
"""
    issue_data = parse_issue_content(content)
    assert issue_data is not None
    assert issue_data.title == "Test Issue Title"
    assert issue_data.body == "This is the body of the test issue.\nIt can span multiple lines."
    assert issue_data.labels == ["bug", "documentation"]
    assert issue_data.assignees == ["octocat", "monalisa"]


def test_parse_issue_content_no_front_matter():
    """
    Test that parse_issue_content returns None when no YAML Front Matter is present.
    """
    content = """
This is just a body.
No front matter here.
"""
    assert parse_issue_content(content) is None


def test_parse_issue_content_invalid_yaml():
    """
    Test that parse_issue_content returns None for invalid YAML Front Matter.
    """
    content = """
---
title: "Test Issue"
labels: - [bug, documentation] # Invalid YAML syntax
---
This is the body.
"""
    assert parse_issue_content(content) is None


def test_parse_issue_content_missing_title():
    """
    Test that parse_issue_content returns None if title is missing from Front Matter.
    """
    content = """
---
labels: ["bug"]
assignees: ["octocat"]
---
Body without title.
"""
    assert parse_issue_content(content) is None


def test_parse_issue_content_empty_labels_and_assignees():
    """
    Test that parse_issue_content handles empty labels and assignees gracefully.
    """
    content = """
---
title: "Another Test"
---
Body with no labels or assignees.
"""
    issue_data = parse_issue_content(content)
    assert issue_data is not None
    assert issue_data.title == "Another Test"
    assert issue_data.labels == []
    assert issue_data.assignees == []


def test_parse_issue_content_non_string_labels_or_assignees():
    """
    Test that parse_issue_content filters out non-string labels or assignees.
    """
    content = """
---
title: "Invalid Types"
labels: ["bug", 123, "feature"]
assignees: ["user1", {"name": "user2"}]
---
Body.
"""
    issue_data = parse_issue_content(content)
    assert issue_data is not None
    assert issue_data.labels == ["bug", "feature"] # 123 should be filtered out
    assert issue_data.assignees == ["user1"] # {"name": "user2"} should be filtered out


# New tests for IssueCreationService
class TestIssueCreationService:

    @pytest.fixture
    def mock_github_service(self):
        return Mock()

    @pytest.fixture
    def issue_creation_service(self, mock_github_service):
        return IssueCreationService(mock_github_service)

    def test_create_issues_from_inbox_success(self, issue_creation_service, mock_github_service):
        # Setup mock for get_pr_files
        mock_pr_file = Mock()
        mock_pr_file.filename = "_in_box/test_issue.md"
        mock_pr_file.sha = "file_sha"
        mock_github_service.get_pr_files.return_value = [mock_pr_file]

        # Setup mock for github_service.get_file_content
        file_content = """
---
title: "Test Issue"
labels: ["bug"]
assignees: ["user"]
---
Test Body
"""
        mock_github_service.get_file_content.return_value = file_content

        # Setup mock for github_service.create_issue
        mock_issue = Mock()
        mock_issue.number = 123
        mock_github_service.create_issue.return_value = mock_issue

        # Run the method
        issue_creation_service.create_issues_from_inbox(pull_number=1)

        # Assertions
        mock_github_service.get_pr_files.assert_called_once_with(1)
        mock_github_service.get_file_content.assert_called_once_with("_in_box/test_issue.md", "file_sha")
        mock_github_service.create_issue.assert_called_once_with(title="Test Issue", body="Test Body", labels=["bug"], assignees=["user"])

        mock_github_service.move_file.assert_called_once()
        args, _ = mock_github_service.move_file.call_args
        assert args[0] == "_in_box/test_issue.md"
        assert args[1].startswith("_done_box/test_issue_")
        assert args[1].endswith(".md")
        assert "feat: Move _in_box/test_issue.md to" in args[2]
        assert f"after issue #{mock_issue.number} creation" in args[2]
        assert args[3] == file_content

    def test_create_issues_from_inbox_no_files(self, issue_creation_service, mock_github_service):
        mock_github_service.get_pr_files.return_value = []
        issue_creation_service.create_issues_from_inbox(pull_number=1)
        mock_github_service.get_pr_files.assert_called_once_with(1)
        mock_github_service.create_issue.assert_not_called()

    def test_create_issues_from_inbox_failure_to_parse(self, issue_creation_service, mock_github_service):
        mock_pr_file = Mock()
        mock_pr_file.filename = "_in_box/bad_issue.md"
        mock_pr_file.sha = "file_sha"
        mock_github_service.get_pr_files.return_value = [mock_pr_file]

        mock_github_service.get_file_content.return_value = "invalid content"

        # Run the method
        issue_creation_service.create_issues_from_inbox(pull_number=1)

        # Assertions
        mock_github_service.get_file_content.assert_called_once_with("_in_box/bad_issue.md", "file_sha")
        mock_github_service.create_issue.assert_not_called()

        mock_github_service.move_file.assert_called_once()
        args, _ = mock_github_service.move_file.call_args
        assert args[0] == "_in_box/bad_issue.md"
        assert args[1].startswith("_failed_box/bad_issue_")
        assert args[1].endswith(".md")
        assert "fix: Move _in_box/bad_issue.md to" in args[2]
        assert "due to error" in args[2]

    def test_create_issues_from_inbox_issue_creation_failure(self, issue_creation_service, mock_github_service):
        mock_pr_file = Mock()
        mock_pr_file.filename = "_in_box/error_issue.md"
        mock_pr_file.sha = "file_sha"
        mock_github_service.get_pr_files.return_value = [mock_pr_file]

        file_content = """
---
title: "Error Issue"
---
Body
"""
        mock_github_service.get_file_content.return_value = file_content
        mock_github_service.create_issue.side_effect = Exception("GitHub API Error")

        # Run the method
        issue_creation_service.create_issues_from_inbox(pull_number=1)

        # Assertions
        mock_github_service.create_issue.assert_called_once()

        mock_github_service.move_file.assert_called_once()
        args, _ = mock_github_service.move_file.call_args
        assert args[0] == "_in_box/error_issue.md"
        assert args[1].startswith("_failed_box/error_issue_")
        assert args[1].endswith(".md")
        assert "fix: Move _in_box/error_issue.md to" in args[2]
        assert "due to error" in args[2]
        assert args[3] == file_content
