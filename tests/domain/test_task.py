import textwrap

import pytest

from github_broker.domain.task import Task


@pytest.mark.unit
@pytest.mark.parametrize(
    "body, expected",
    [
        ("## 成果物\n- 何か", True),
        ("\n## 成果物\n\n- item1", True),
        ("some text\n## 成果物\n- item1", True),
        ("## 成果物", True),  # セクションヘッダがあればOK
        ("##せいかぶつ\n- item1", False),  # 日本語の全角・半角を区別
        ("成果物\n- item1", False),  # "## "がない
        ("No deliverables section", False),
        ("", False),
    ],
)
def test_is_assignable(body, expected):
    """Issueの本文に「成果物」セクションが含まれているかどうかに基づいて、タスクの割り当て可能性をテストします。"""
    # Arrange
    task = Task(
        issue_id=1,
        title="Test Task",
        body=body,
        html_url="http://example.com",
        labels=["test"],
    )

    # Act
    result = task.is_assignable()

    # Assert
    assert result == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "body, expected_branch_name",
    [
        ("## ブランチ名\n`feature/branch-1`", "feature/branch-1"),
        ("\n\n## ブランチ名\n\n`feature/branch-2`\n", "feature/branch-2"),
        ("some text\n## ブランチ名 `feature/branch-3`", "feature/branch-3"),
        ("## ブランチ名 feature/branch-4", "feature/branch-4"),
        (
            "## ブランチ名 (Branch name)\nbugfix/fix-prompt-generation-logic",
            "bugfix/fix-prompt-generation-logic",
        ),
        ("no branch name section", None),
        ("", None),
    ],
)
def test_extract_branch_name(body, expected_branch_name):
    """Issueの本文からブランチ名を正しく抽出できるかテストします。"""
    task = Task(
        issue_id=1, title="Test", body=textwrap.dedent(body), html_url="", labels=[]
    )
    result = task.extract_branch_name()
    assert result == expected_branch_name


@pytest.mark.unit
def test_task_type_enum():
    """TaskType Enumに必要な値がすべて存在することを確認します。"""
    # Arrange
    from github_broker.domain.task import TaskType

    # Assert
    assert TaskType.DEVELOPMENT.value == "development"
    assert TaskType.REVIEW.value == "review"
    assert TaskType.FIX.value == "fix"
    assert len(TaskType) == 3
