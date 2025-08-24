import os
import textwrap
from unittest.mock import MagicMock, patch

import pytest
from github import GithubException
from github.Issue import Issue
from github.Label import Label

from github_broker.application.task_service import TaskService
from github_broker.domain.task import Task
from github_broker.interface.models import TaskResponse


@pytest.fixture
def mock_redis_client():
    """Redisクライアントのモックを提供します。"""
    return MagicMock()


@pytest.fixture
def mock_github_client():
    """GitHubクライアントのモックを提供します。"""
    return MagicMock()


@pytest.fixture
def mock_gemini_client():
    """Geminiクライアントのモックを提供します。"""
    return MagicMock()


@pytest.fixture
def task_service(mock_redis_client, mock_github_client, mock_gemini_client):
    """TaskServiceのテストインスタンスを提供します。"""
    with patch.dict(os.environ, {"GITHUB_REPOSITORY": "test/repo"}):
        return TaskService(
            redis_client=mock_redis_client,
            github_client=mock_github_client,
            gemini_client=mock_gemini_client,
        )


@pytest.fixture
def issue_with_branch():
    """ブランチ名を持つIssueのモックを提供します。"""
    issue = MagicMock(spec=Issue)
    issue.id = 1
    issue.number = 123
    issue.title = "ブランチ名付きのテストIssue"
    issue.body = textwrap.dedent("""
        これはテストIssueです。

        ## ブランチ名
        `feature/issue-123-test`""")
    issue.html_url = "https://github.com/test/repo/issues/123"
    label = MagicMock(spec=Label)
    label.name = "bug"
    issue.labels = [label]
    return issue


@pytest.fixture
def issue_without_branch():
    """ブランチ名を持たないIssueのモックを提供します。"""
    issue = MagicMock(spec=Issue)
    issue.id = 2
    issue.number = 456
    issue.title = "ブランチ名なしのテストIssue"
    issue.body = "このIssueにはブランチ名がありません。"
    issue.html_url = "https://github.com/test/repo/issues/456"
    issue.labels = []
    return issue


def test_request_task_no_open_issues(task_service, mock_github_client):
    """オープンなIssueがない場合にNoneが返されることをテストします。"""
    mock_github_client.get_open_issues.return_value = []
    result = task_service.request_task("test-agent")
    assert result is None


def test_request_task_no_assignable_issues(
    task_service, mock_github_client, issue_without_branch
):
    """ブランチ名を持つIssueがない場合にNoneが返されることをテストします。"""
    mock_github_client.get_open_issues.return_value = [issue_without_branch]
    result = task_service.request_task("test-agent")
    assert result is None


def test_request_task_skips_issue_without_branch_name(
    task_service,
    mock_redis_client,
    mock_github_client,
    issue_with_branch,
    issue_without_branch,
):
    """サービスがブランチ名のないIssueをスキップし、次のIssueを見つけることをテストします。"""
    mock_github_client.get_open_issues.return_value = [
        issue_without_branch,
        issue_with_branch,
    ]
    mock_redis_client.acquire_lock.return_value = True

    result = task_service.request_task("test-agent")

    assert isinstance(result, TaskResponse)
    assert result.issue_id == 123  # 2番目のIssue
    mock_redis_client.acquire_lock.assert_called_once_with(
        f"issue_lock_{issue_with_branch.number}", "locked", timeout=600
    )


def test_request_task_skips_locked_issue(
    task_service,
    mock_redis_client,
    mock_github_client,
    mock_gemini_client,
    issue_with_branch,
):
    """サービスがロックされたIssueをスキップし、次のIssueを見つけることをテストします。"""
    issue2_with_branch = MagicMock(spec=Issue)
    issue2_with_branch.id = 3
    issue2_with_branch.number = 789
    issue2_with_branch.title = "2番目のテストIssue"
    issue2_with_branch.body = textwrap.dedent("""
        ## ブランチ名
        `feature/issue-789-another`""")
    issue2_with_branch.html_url = "https://github.com/test/repo/issues/789"
    issue2_with_branch.labels = []

    mock_github_client.get_open_issues.return_value = [
        issue_with_branch,
        issue2_with_branch,
    ]
    # 最初のIssueのロックに失敗し、2番目で成功する
    mock_redis_client.acquire_lock.side_effect = [False, True]
    mock_gemini_client.select_best_issue_id.return_value = issue2_with_branch.number

    result = task_service.request_task("test-agent")

    assert result is None
    assert mock_redis_client.acquire_lock.call_count == 1
    mock_redis_client.acquire_lock.assert_called_once_with(
        f"issue_lock_{issue2_with_branch.number}", "locked", timeout=600
    )
    mock_gemini_client.select_best_issue_id.assert_called_once()


@patch("time.sleep", return_value=None)
def test_request_task_success(
    mock_sleep, task_service, mock_redis_client, mock_github_client, issue_with_branch
):
    """タスクの割り当てが成功するケースをテストします。"""
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.get_open_issues.return_value = [issue_with_branch]

    result = task_service.request_task("test-agent")

    assert isinstance(result, TaskResponse)
    assert result.issue_id == 123
    assert result.title == "ブランチ名付きのテストIssue"
    assert result.branch_name == "feature/issue-123-test"
    mock_redis_client.acquire_lock.assert_called_once_with(
        f"issue_lock_{issue_with_branch.number}", "locked", timeout=600
    )
    mock_github_client.add_label.assert_any_call("test/repo", 123, "in-progress")
    mock_github_client.add_label.assert_any_call("test/repo", 123, "test-agent")
    mock_github_client.create_branch.assert_called_once_with(
        "test/repo", "feature/issue-123-test"
    )
    mock_sleep.assert_called_once_with(15)


def test_request_task_exception_after_lock(
    task_service, mock_redis_client, mock_github_client, issue_with_branch
):
    """ロック取得後に例外が発生した場合にロックが解放されることをテストします。"""
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.get_open_issues.return_value = [issue_with_branch]
    mock_github_client.add_label.side_effect = GithubException(
        status=500, data={}, headers=None
    )

    with pytest.raises(GithubException):
        task_service.request_task("test-agent")

    mock_redis_client.release_lock.assert_called_once_with(
        f"issue_lock_{issue_with_branch.number}"
    )


def test_extract_branch_name_from_issue_found():
    """Issue本文からブランチ名が正しく抽出されることをテストします。"""
    body = textwrap.dedent("""
        いくつかのテキスト
        ## ブランチ名
        `feature/issue-42-new-feature`
        追加のテキスト""")
    task = Task(issue_id=42, title="", body=body, html_url="", labels=[])
    branch_name = task.extract_branch_name()
    assert branch_name == "feature/issue-42-new-feature"


def test_extract_branch_name_from_issue_not_found():
    """本文にブランチ名が見つからない場合にNoneが返されることをテストします。"""
    body = "ブランチ名のないテキスト"
    task = Task(issue_id=42, title="", body=body, html_url="", labels=[])
    branch_name = task.extract_branch_name()
    assert branch_name is None


def test_extract_branch_name_with_issue_xx_replacement():
    """'issue-xx'が実際のIssue番号に正しく置換されることをテストします。"""
    body = textwrap.dedent("""
        ## ブランチ名
        `feature/issue-xx-cool-feature`""")
    task = Task(issue_id=99, title="", body=body, html_url="", labels=[])
    branch_name = task.extract_branch_name()
    assert branch_name == "feature/issue-99-cool-feature"


def test_complete_previous_task_success(task_service, mock_github_client):
    """前タスクの完了処理が成功するケースをテストします。"""
    mock_issue = MagicMock(spec=Issue)
    mock_issue.number = 100
    mock_issue.labels = [
        MagicMock(name="in-progress", spec=Label),
        MagicMock(name="test-agent", spec=Label),
        MagicMock(name="bug", spec=Label),
    ]
    mock_github_client.search_issues.return_value = [mock_issue]

    agent_id = "test-agent"
    task_service.complete_previous_task(agent_id)

    mock_github_client.search_issues.assert_called_once_with(
        repo_name="test/repo", labels=["in-progress", agent_id]
    )
    mock_github_client.update_issue.assert_called_once_with(
        repo_name="test/repo",
        issue_id=100,
        remove_labels=["in-progress", "test-agent"],
        add_labels=["needs-review"],
    )


@patch("time.sleep", return_value=None)
def test_complete_previous_task_no_previous_task(
    mock_sleep, task_service, mock_github_client
):
    """前タスクがない場合に何も処理されないことをテストします。"""
    mock_github_client.search_issues.return_value = []

    agent_id = "test-agent"
    task_service.complete_previous_task(agent_id)

    mock_github_client.search_issues.assert_called_once_with(
        repo_name="test/repo", labels=["in-progress", agent_id]
    )
    mock_github_client.update_issue.assert_not_called()
    mock_sleep.assert_not_called()
