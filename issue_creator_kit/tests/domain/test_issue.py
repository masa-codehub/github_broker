from issue_creator_kit.domain.issue import IssueData


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
