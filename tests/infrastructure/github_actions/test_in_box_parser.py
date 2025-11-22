import pytest

from github_broker.infrastructure.github_actions.in_box_parser import InboxParser


class TestInboxParser:

    @pytest.fixture
    def parser(self):
        return InboxParser()

    def test_parse_simple_issue_file(self, parser):
        content = """# My Test Issue
This is the body of my test issue.
"""
        result = parser.parse_issue_file(content)
        assert result["title"] == "My Test Issue"
        assert result["body"] == "This is the body of my test issue."
        assert result["labels"] == []
        assert result["assignees"] == []

    def test_parse_issue_file_with_front_matter_and_labels(self, parser):
        content = """---
labels:
  - bug
  - feature
---
# Issue with Labels
This issue has labels.
"""
        result = parser.parse_issue_file(content)
        assert result["title"] == "Issue with Labels"
        assert result["body"] == "This issue has labels."
        assert result["labels"] == ["bug", "feature"]
        assert result["assignees"] == []

    def test_parse_issue_file_with_front_matter_and_assignees(self, parser):
        content = """---
assignees:
  - user1
  - user2
---
# Issue with Assignees
This issue has assignees.
"""
        result = parser.parse_issue_file(content)
        assert result["title"] == "Issue with Assignees"
        assert result["body"] == "This issue has assignees."
        assert result["labels"] == []
        assert result["assignees"] == ["user1", "user2"]

    def test_parse_issue_file_with_front_matter_labels_and_assignees(self, parser):
        content = """---
labels:
  - enhancement
assignees:
  - user3
---
# Full Featured Issue
This is a comprehensive issue.
"""
        result = parser.parse_issue_file(content)
        assert result["title"] == "Full Featured Issue"
        assert result["body"] == "This is a comprehensive issue."
        assert result["labels"] == ["enhancement"]
        assert result["assignees"] == ["user3"]

    def test_parse_issue_file_no_title(self, parser):
        content = """This is an issue with no explicit title.
It should all be considered body.
"""
        result = parser.parse_issue_file(content)
        assert result["title"] == ""
        assert result["body"] == "This is an issue with no explicit title.\nIt should all be considered body."
        assert result["labels"] == []
        assert result["assignees"] == []

    def test_parse_empty_file(self, parser):
        content = ""
        result = parser.parse_issue_file(content)
        assert result["title"] == ""
        assert result["body"] == ""
        assert result["labels"] == []
        assert result["assignees"] == []

    def test_parse_only_front_matter(self, parser):
        content = """---
labels:
  - critical
---
"""
        result = parser.parse_issue_file(content)
        assert result["title"] == ""
        assert result["body"] == ""
        assert result["labels"] == ["critical"]
        assert result["assignees"] == []
