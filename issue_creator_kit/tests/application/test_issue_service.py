from issue_creator_kit.application.issue_service import (
    parse_issue_content,
)
from issue_creator_kit.domain.issue import IssueData


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


def test_issue_data_init():
    """
    Test that IssueData initializes correctly with default and provided values.
    """
    issue_data = IssueData(title="Title", body="Body")
    assert issue_data.title == "Title"
    assert issue_data.body == "Body"
    assert issue_data.labels == []
    assert issue_data.assignees == []

    issue_data_full = IssueData(title="Full Title", body="Full Body", labels=["label1"], assignees=["assignee1"])
    assert issue_data_full.title == "Full Title"
    assert issue_data_full.body == "Full Body"
    assert issue_data_full.labels == ["label1"]
    assert issue_data_full.assignees == ["assignee1"]
