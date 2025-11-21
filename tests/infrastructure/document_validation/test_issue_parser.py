from github_broker.infrastructure.document_validation.issue_parser import (
    IssueData,
    parse_issue_content,
)


def test_parse_issue_content_returns_none_for_dummy_implementation():
    """
    Test that the dummy parse_issue_content implementation returns None. (Red phase)
    """
    content = """
---
title: "Test Issue"
labels: ["bug", "documentation"]
assignees: ["octocat"]
---
This is the body of the test issue.
"""
    assert parse_issue_content(content) is None

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
