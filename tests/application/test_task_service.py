import json
import logging
import threading
from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from github_broker.application.task_service import OPEN_ISSUES_CACHE_KEY, TaskService


@pytest.fixture
def mock_redis_client():
    """Redisクライアントのモックを提供します。"""
    return MagicMock()


@pytest.fixture
def mock_github_client():
    """GitHubクライアントのモックを提供します。"""
    return MagicMock()


@pytest.fixture
def task_service(mock_redis_client, mock_github_client):
    """TaskServiceのテストインスタンスを提供します。"""
    mock_settings = MagicMock()
    mock_settings.GITHUB_REPOSITORY = "test/repo"
    mock_settings.GITHUB_INDEXING_WAIT_SECONDS = 0
    mock_settings.POLLING_INTERVAL_SECONDS = 0.1
    return TaskService(
        redis_client=mock_redis_client,
        github_client=mock_github_client,
        settings=mock_settings,
    )


def create_mock_issue(
    number,
    title,
    body,
    labels,
    html_url_base="https://github.com/test/repo/issues",
    has_branch_name: bool = True,
):
    """テスト用のIssue辞書を生成するヘルパー関数。"""
    full_body = body
    if has_branch_name:
        full_body += f"""

## ブランチ名
`feature/issue-{number}`"""

    return {
        "number": number,
        "title": title,
        "body": full_body,
        "html_url": f"{html_url_base}/{number}",
        "labels": [{"name": label} for label in labels],
    }


@pytest.mark.unit
def test_start_polling_fetches_and_caches_issues(
    task_service, mock_github_client, mock_redis_client
):
    """start_pollingがIssueを取得し、単一キーでRedisにキャッシュすることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(number=1, title="Poll Task 1", body="", labels=["bug"])
    issue2 = create_mock_issue(
        number=2, title="Poll Task 2", body="", labels=["feature"]
    )
    mock_issues = [issue1, issue2]
    mock_github_client.get_open_issues.return_value = mock_issues

    stop_event = threading.Event()

    def stop_loop(*args, **kwargs):
        if mock_github_client.get_open_issues.call_count == 1:
            stop_event.set()
        return mock_issues

    mock_github_client.get_open_issues.side_effect = stop_loop

    # Act
    polling_thread = threading.Thread(
        target=task_service.start_polling, args=(stop_event,)
    )
    polling_thread.start()
    polling_thread.join(timeout=5)

    # Assert
    mock_github_client.get_open_issues.assert_called_once()
    mock_redis_client.set_value.assert_called_once_with(
        OPEN_ISSUES_CACHE_KEY, json.dumps(mock_issues)
    )


@pytest.mark.unit
def test_start_polling_caches_empty_list_when_no_issues(
    task_service, mock_github_client, mock_redis_client
):
    """start_pollingがIssueがない場合に空のリストをキャッシュすることをテストします。"""
    # Arrange
    mock_github_client.get_open_issues.return_value = []
    stop_event = threading.Event()

    def stop_loop(*args, **kwargs):
        if mock_github_client.get_open_issues.call_count == 1:
            stop_event.set()
        return []

    mock_github_client.get_open_issues.side_effect = stop_loop

    # Act
    polling_thread = threading.Thread(
        target=task_service.start_polling, args=(stop_event,)
    )
    polling_thread.start()
    polling_thread.join(timeout=5)

    # Assert
    mock_github_client.get_open_issues.assert_called_once()
    mock_redis_client.set_value.assert_called_once_with(
        OPEN_ISSUES_CACHE_KEY, json.dumps([])
    )


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_request_task_selects_by_role_from_cache(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """エージェントの役割（role）に一致するラベルを持つIssueがキャッシュから選択されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1,
        title="Irrelevant Task",
        body="""
## 成果物
- README.md""",
        labels=["documentation"],
    )
    issue2 = create_mock_issue(
        number=2,
        title="Backend Task",
        body="""
## 成果物
- feature.py""",
        labels=["feature", "BACKENDCODER"],
    )
    cached_issues = [issue1, issue2]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    agent_role = "BACKENDCODER"

    # Act
    result = task_service.request_task(agent_id="test-agent", agent_role=agent_role)

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.get_value.assert_called_once_with(OPEN_ISSUES_CACHE_KEY)
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_2", "locked", timeout=600
    )


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_request_task_no_matching_issue(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """エージェントの役割に一致するIssueがない場合にNoneが返されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1, title="Docs", body="", labels=["documentation"]
    )
    cached_issues = [issue1]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []
    agent_role = "BACKENDCODER"

    # Act
    result = task_service.request_task(agent_id="test-agent", agent_role=agent_role)

    # Assert
    assert result is None
    mock_redis_client.get_value.assert_called_once_with(OPEN_ISSUES_CACHE_KEY)


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_request_task_excludes_needs_review_label(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """'needs-review'ラベルを持つIssueがタスク割り当てから除外されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1,
        title="Task Needs Review",
        body="""
## 成果物
- review.py""",
        labels=["BACKENDCODER", "needs-review"],
    )
    issue2 = create_mock_issue(
        number=2,
        title="Assignable Task",
        body="""
## 成果物
- assign.py""",
        labels=["BACKENDCODER"],
    )
    cached_issues = [issue1, issue2]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    # Act
    result = task_service.request_task(agent_id="test-agent", agent_role="BACKENDCODER")

    # Assert
    assert result is not None
    assert result.issue_id == 2


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_request_task_completes_previous_task(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """
    request_taskが前タスクの完了処理を呼び出し、Issueが更新されることをテストします。
    """
    # Arrange
    prev_issue = create_mock_issue(
        number=101,
        title="Previous Task",
        body="",
        labels=["in-progress", "test-agent"],
    )
    new_issue = create_mock_issue(
        number=102,
        title="New Task",
        body="## 成果物\n- new.py",
        labels=["BACKENDCODER"],
    )
    cached_issues = [prev_issue, new_issue]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_redis_client.acquire_lock.return_value = True

    agent_id = "test-agent"
    agent_role = "BACKENDCODER"

    # Act
    result = task_service.request_task(agent_id=agent_id, agent_role=agent_role)

    # Assert
    mock_github_client.update_issue.assert_called_once_with(
        issue_id=prev_issue["number"],
        remove_labels=["in-progress", agent_id],
        add_labels=["needs-review"],
    )
    assert result is not None
    assert result.issue_id == new_issue["number"]


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_find_first_assignable_task_exception_releases_lock(
    mock_sleep, task_service, mock_github_client, mock_redis_client
):
    """
    _find_first_assignable_task内で例外が発生した場合にロックが解放されることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""
## 成果物
- test.py""",
        labels=["BACKENDCODER"],
    )
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.add_label.side_effect = Exception("GitHub API Error")

    candidate_issues = [issue]
    agent_id = "test-agent"

    # Act & Assert
    with pytest.raises(Exception, match="GitHub API Error"):
        task_service._find_first_assignable_task(candidate_issues, agent_id)

    mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_find_first_assignable_task_create_branch_exception_releases_lock(
    mock_sleep, task_service, mock_github_client, mock_redis_client
):
    """
    _find_first_assignable_task内でcreate_branchが例外を発生させた場合にロックが解放されることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""
## 成果物
- test.py""",
        labels=["BACKENDCODER"],
    )
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.create_branch.side_effect = Exception("Branch Creation Error")

    candidate_issues = [issue]
    agent_id = "test-agent"

    # Act & Assert
    with pytest.raises(Exception, match="Branch Creation Error"):
        task_service._find_first_assignable_task(candidate_issues, agent_id)

    mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_find_first_assignable_task_rollback_labels_on_branch_creation_failure(
    mock_sleep, task_service, mock_github_client, mock_redis_client, caplog
):
    """
    _find_first_assignable_task内でcreate_branchが例外を発生させた場合に、
    付与されたラベルがロールバックされることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""
## 成果物
- test.py""",
        labels=["BACKENDCODER"],
    )
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.create_branch.side_effect = GithubException(
        status=422, data="Branch already exists"
    )

    candidate_issues = [issue]
    agent_id = "test-agent"

    with caplog.at_level(logging.ERROR):
        # Act & Assert
        with pytest.raises(GithubException, match="Branch already exists"):
            task_service._find_first_assignable_task(candidate_issues, agent_id)

        # Assert
        # ロックが解放されたことを確認
        mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")
        # 付与されたラベルが削除されたことを確認
        mock_github_client.update_issue.assert_called_once_with(
            issue_id=issue["number"], remove_labels=["in-progress", agent_id]
        )
        mock_github_client.remove_label.assert_not_called()


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_find_first_assignable_task_rollback_failure_logs_error(
    mock_sleep, task_service, mock_github_client, mock_redis_client, caplog
):
    """
    _find_first_assignable_task内でcreate_branchが例外を発生させ、
    さらにラベルのロールバックも失敗した場合に、エラーがログに記録されることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""
## 成果物
- test.py""",
        labels=["BACKENDCODER"],
    )
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.create_branch.side_effect = GithubException(
        status=422, data="Branch already exists"
    )
    mock_github_client.update_issue.side_effect = Exception("Rollback Error")

    candidate_issues = [issue]
    agent_id = "test-agent"

    with caplog.at_level(logging.ERROR):
        # Act & Assert
        with pytest.raises(GithubException, match="Branch already exists"):
            task_service._find_first_assignable_task(candidate_issues, agent_id)

        # Assert
        # ロックが解放されたことを確認
        mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")
        # ロールバック処理自体でエラーが発生した場合もログに記録されることを確認
        assert "Failed to rollback labels for issue #1: Rollback Error" in caplog.text
        # update_issueが呼び出されたことを確認
        mock_github_client.update_issue.assert_called_once()


@pytest.mark.unit
def test_find_first_assignable_task_skips_non_assignable(
    task_service, mock_redis_client
):
    """is_assignable()がFalseを返すIssueをスキップすることをテストします。"""
    # Arrange
    issue_not_assignable = create_mock_issue(
        number=1,
        title="Not Assignable",
        body="No deliverables section",
        labels=["BACKENDCODER"],
        has_branch_name=True,
    )
    issue_assignable = create_mock_issue(
        number=2, title="Assignable", body="## 成果物\n- work", labels=["BACKENDCODER"]
    )
    candidate_issues = [issue_not_assignable, issue_assignable]
    mock_redis_client.acquire_lock.return_value = True

    # Act
    result = task_service._find_first_assignable_task(candidate_issues, "test-agent")

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_2", "locked", timeout=600
    )


@pytest.mark.unit
def test_find_first_assignable_task_skips_no_branch_name(
    task_service, mock_redis_client
):
    """ブランチ名が本文にないIssueをスキップすることをテストします。"""
    # Arrange
    issue_no_branch = create_mock_issue(
        number=1,
        title="No Branch",
        body="## 成果物\n- work",
        labels=["BACKENDCODER"],
        has_branch_name=False,
    )
    issue_with_branch = create_mock_issue(
        number=2,
        title="With Branch",
        body="## 成果物\n- work",
        labels=["BACKENDCODER"],
        has_branch_name=True,
    )
    candidate_issues = [issue_no_branch, issue_with_branch]
    mock_redis_client.acquire_lock.return_value = True

    # Act
    result = task_service._find_first_assignable_task(candidate_issues, "test-agent")

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_2", "locked", timeout=600
    )


@pytest.mark.unit
def test_find_first_assignable_task_skips_locked_issue(task_service, mock_redis_client):
    """RedisでロックされているIssueをスキップすることをテストします。"""
    # Arrange
    issue_locked = create_mock_issue(
        number=1,
        title="Locked Issue",
        body="## 成果物\n- work",
        labels=["BACKENDCODER"],
    )
    issue_unlocked = create_mock_issue(
        number=2,
        title="Unlocked Issue",
        body="## 成果物\n- work",
        labels=["BACKENDCODER"],
    )
    candidate_issues = [issue_locked, issue_unlocked]
    mock_redis_client.acquire_lock.side_effect = [False, True]

    # Act
    result = task_service._find_first_assignable_task(candidate_issues, "test-agent")

    # Assert
    assert result is not None
    assert result.issue_id == 2
    assert mock_redis_client.acquire_lock.call_count == 2
    mock_redis_client.acquire_lock.assert_any_call(
        "issue_lock_1", "locked", timeout=600
    )
    mock_redis_client.acquire_lock.assert_any_call(
        "issue_lock_2", "locked", timeout=600
    )


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_no_matching_role_candidates(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """オープンなIssueはあるが、役割に合う候補がない場合のテスト。"""
    # Arrange
    issue_other_role = create_mock_issue(
        number=1,
        title="Other Role Task",
        body="## 成果物\n- work",
        labels=["FRONTENDCODER"],
    )
    cached_issues = [issue_other_role]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []

    # Act
    result = task_service.request_task(agent_id="test-agent", agent_role="BACKENDCODER")

    # Assert
    assert result is None


@pytest.mark.unit
@patch("time.sleep", return_value=None)
@pytest.mark.parametrize(
    "exception_to_raise, expected_log_message",
    [
        (
            GithubException(status=500, data="Test Error 1"),
            "Failed to update issue #101",
        ),
        (
            Exception("Unexpected Error"),
            "An unexpected error occurred while updating issue #101",
        ),
    ],
    ids=["github_exception", "unexpected_exception"],
)
def test_complete_previous_task_handles_exceptions(
    mock_sleep,
    task_service,
    mock_redis_client,
    mock_github_client,
    caplog,
    exception_to_raise,
    expected_log_message,
):
    """
    complete_previous_task内で例外が発生しても、処理が続行されることをテストします。
    """
    # Arrange
    prev_issue_1 = create_mock_issue(
        number=101,
        title="Previous Task 1",
        body="",
        labels=["in-progress", "test-agent"],
    )
    prev_issue_2 = create_mock_issue(
        number=102,
        title="Previous Task 2",
        body="",
        labels=["in-progress", "test-agent"],
    )
    new_issue = create_mock_issue(
        number=103,
        title="New Task",
        body="## 成果物\n- new.py",
        labels=["BACKENDCODER"],
    )
    cached_issues = [prev_issue_1, prev_issue_2, new_issue]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_redis_client.acquire_lock.return_value = True

    agent_id = "test-agent"
    agent_role = "BACKENDCODER"

    # 最初のupdate_issueで例外を発生させ、2番目は成功させる
    mock_github_client.update_issue.side_effect = [
        exception_to_raise,
        None,  # 2番目の呼び出しは成功
    ]

    with caplog.at_level(logging.ERROR):
        # Act
        result = task_service.request_task(agent_id=agent_id, agent_role=agent_role)

        # Assert
        # update_issueが2回呼び出されたことを確認
        assert mock_github_client.update_issue.call_count == 2
        # 最初のIssueでエラーがログに記録されたことを確認
        assert expected_log_message in caplog.text
        # 2番目のIssueの更新が成功したことを確認
        mock_github_client.update_issue.assert_called_with(
            issue_id=prev_issue_2["number"],
            remove_labels=["in-progress", agent_id],
            add_labels=["needs-review"],
        )
        # 新しいタスクが正常に返されたことを確認
        assert result is not None
        assert result.issue_id == new_issue["number"]
