import json
import logging
import threading
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from github import GithubException

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor
from github_broker.interface.models import TaskType


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
    mock_settings.POLLING_INTERVAL_SECONDS = 60
    mock_settings.LONG_POLLING_CHECK_INTERVAL = 5
    mock_settings.REVIEW_TIMEOUT_MINUTES = 10

    mock_gemini_executor_instance = MagicMock(spec=GeminiExecutor)
    mock_gemini_executor_instance.build_prompt.return_value = "Generated Prompt"
    mock_gemini_executor_instance.build_code_review_prompt.return_value = (
        "Generated Code Review Prompt"
    )
    mock_gemini_executor_instance.execute = AsyncMock(
        return_value="Gemini Executor Output"
    )

    return TaskService(
        redis_client=mock_redis_client,
        github_client=mock_github_client,
        settings=mock_settings,
        gemini_executor=mock_gemini_executor_instance,
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
        full_body += f"\n\n## ブランチ名\n`feature/issue-{number}`"

    return {
        "number": number,
        "title": title,
        "body": full_body,
        "html_url": f"{html_url_base}/{number}",
        "labels": [{"name": label} for label in labels],
    }


def create_mock_pr(number, created_at):
    """テスト用のPull Requestオブジェクトのモックを生成するヘルパー関数。"""
    mock_pr = MagicMock()
    mock_pr.number = number
    mock_pr.created_at = created_at
    return mock_pr


@pytest.mark.unit
def test_start_polling_fetches_and_caches_issues(
    task_service, mock_github_client, mock_redis_client
):
    """start_pollingがIssueを取得し、RedisClientのsync_issuesを呼び出すことをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1, title="Poll Task 1", body="", labels=["bug", "P1"]
    )
    issue2 = create_mock_issue(
        number=2, title="Poll Task 2", body="", labels=["feature", "P1"]
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
    mock_redis_client.sync_issues.assert_called_once_with(mock_issues)


@pytest.mark.unit
def test_start_polling_caches_empty_list_when_no_issues(
    task_service, mock_github_client, mock_redis_client
):
    """start_pollingがIssueがない場合に、空のリストでsync_issuesを呼び出すことをテストします。"""
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
    mock_redis_client.sync_issues.assert_called_once_with([])


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_selects_and_sets_required_role_from_cache(
    task_service, mock_redis_client, mock_github_client
):
    """RedisキャッシュからIssueを正しく選択し、required_roleを正しく設定できることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1, title="Docs", body="", labels=["documentation", "P1"]
    )
    issue2 = create_mock_issue(
        number=2,
        title="Backend Task",
        body="""## 成果物\n- test.py""",
        labels=["feature", "BACKENDCODER", "P1"],
    )
    cached_issues = [issue1, issue2]
    issue_keys = [f"issue:{issue['number']}" for issue in cached_issues]
    mock_redis_client.get_keys_by_pattern.return_value = issue_keys
    mock_redis_client.get_values.return_value = [
        json.dumps(issue) for issue in cached_issues
    ]
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    agent_id = "test-agent"

    # Act
    result = await task_service.request_task(agent_id=agent_id)

    # Assert
    assert result is not None
    assert result.issue_id == 2
    assert result.required_role == "BACKENDCODER"
    mock_redis_client.get_keys_by_pattern.assert_called_once_with("issue:*")
    mock_redis_client.get_values.assert_called_once_with(issue_keys)
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_2", agent_id, timeout=600
    )
    task_service.gemini_executor.build_prompt.assert_called_once_with(
        html_url=issue2["html_url"],
        branch_name="feature/issue-2",
    )
    mock_redis_client.set_value.assert_called_once_with(
        f"agent_current_task:{agent_id}", str(issue2["number"]), timeout=3600
    )


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_no_matching_role_label_issue(
    task_service, mock_redis_client, mock_github_client
):
    """Issueに役割ラベルがない場合にNoneが返されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1,
        title="Docs",
        body="""## 成果物\n- docs""",
        labels=["documentation", "P1"],
    )
    cached_issues = [issue1]
    issue_keys = [f"issue:{issue['number']}" for issue in cached_issues]
    mock_redis_client.get_keys_by_pattern.return_value = issue_keys
    mock_redis_client.get_values.return_value = [
        json.dumps(issue) for issue in cached_issues
    ]
    mock_github_client.find_issues_by_labels.return_value = []
    agent_id = "test-agent"

    # Act
    result = await task_service.request_task(agent_id=agent_id)

    # Assert
    assert result is None
    mock_redis_client.get_keys_by_pattern.assert_called_once_with("issue:*")


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_completes_previous_task(
    task_service, mock_redis_client, mock_github_client
):
    """request_taskが前タスクの完了処理を呼び出すことをテストします。"""
    # Arrange
    agent_id = "test-agent"
    prev_issue = create_mock_issue(
        number=1,
        title="Previous Task",
        body="",
        labels=["in-progress", agent_id, "P1"],
    )
    new_issue = create_mock_issue(
        number=2,
        title="New Task",
        body="""## 成果物\n- new.py""",
        labels=["BACKENDCODER", "P1"],
    )
    cached_issues = [new_issue]
    issue_keys = [f"issue:{issue['number']}" for issue in cached_issues]
    mock_redis_client.get_keys_by_pattern.return_value = issue_keys
    mock_redis_client.get_values.return_value = [
        json.dumps(issue) for issue in cached_issues
    ]
    mock_redis_client.acquire_lock.return_value = True

    # Setup GitHub API to return previous issue for completion
    mock_github_client.find_issues_by_labels.return_value = [prev_issue]

    # Act
    result = await task_service.request_task(agent_id=agent_id)

    # Assert
    mock_github_client.find_issues_by_labels.assert_called_once_with(
        labels=["in-progress", agent_id]
    )
    mock_github_client.update_issue.assert_called_once_with(
        issue_id=prev_issue["number"],
        remove_labels=["in-progress", agent_id],
        add_labels=["needs-review"],
    )
    assert result is not None
    assert result.issue_id == new_issue["number"]


@pytest.mark.unit
@pytest.mark.anyio
async def test_find_first_assignable_task_exception_releases_lock(
    task_service, mock_github_client, mock_redis_client
):
    """
    _find_first_assignable_task内で例外が発生した場合にロックが解放されることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""## 成果物\n- test.py""",
        labels=["BACKENDCODER", "P1"],
    )
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.add_label.side_effect = Exception("GitHub API Error")

    candidate_issues = [issue]
    agent_id = "test-agent"

    # Act & Assert
    with pytest.raises(Exception, match="GitHub API Error"):
        await task_service._find_first_assignable_task(candidate_issues, agent_id)

    mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")


@pytest.mark.unit
@pytest.mark.anyio
async def test_find_first_assignable_task_create_branch_exception_releases_lock(
    task_service, mock_github_client, mock_redis_client
):
    """
    _find_first_assignable_task内でcreate_branchが例外を発生させた場合にロックが解放されることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""## 成果物\n- test.py""",
        labels=["BACKENDCODER", "P1"],
    )
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.create_branch.side_effect = Exception("Branch Creation Error")

    candidate_issues = [issue]
    agent_id = "test-agent"

    # Act & Assert
    with pytest.raises(Exception, match="Branch Creation Error"):
        await task_service._find_first_assignable_task(candidate_issues, agent_id)

    mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")


@pytest.mark.unit
@pytest.mark.anyio
async def test_find_first_assignable_task_rollback_labels_on_branch_creation_failure(
    task_service, mock_github_client, mock_redis_client, caplog
):
    """
    _find_first_assignable_task内でcreate_branchが例外を発生させた場合に、
    付与されたラベルがロールバックされることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""## 成果物\n- test.py""",
        labels=["BACKENDCODER", "P1"],
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
            await task_service._find_first_assignable_task(candidate_issues, agent_id)

        mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")
        mock_github_client.update_issue.assert_called_once_with(
            issue_id=issue["number"], remove_labels=["in-progress", agent_id]
        )
        mock_github_client.remove_label.assert_not_called()


@pytest.mark.unit
@pytest.mark.anyio
async def test_find_first_assignable_task_rollback_failure_logs_error(
    task_service, mock_github_client, mock_redis_client, caplog
):
    """
    _find_first_assignable_task内でcreate_branchが例外を発生させ、
    さらにラベルのロールバックも失敗した場合に、エラーがログに記録されることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""## 成果物\n- test.py""",
        labels=["BACKENDCODER", "P1"],
    )
    mock_redis_client.acquire_lock.return_value = True
    mock_github_client.create_branch.side_effect = GithubException(
        status=422, data="Branch already exists"
    )
    mock_github_client.update_issue.side_effect = Exception("Rollback Error")

    candidate_issues = [issue]
    agent_id = "test-agent"

    with caplog.at_level(logging.ERROR):
        with pytest.raises(GithubException, match="Branch already exists"):
            await task_service._find_first_assignable_task(candidate_issues, agent_id)

        assert "Failed to rollback labels" in caplog.text
        mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")
        mock_github_client.update_issue.assert_called_once()


@pytest.mark.unit
@pytest.mark.anyio
async def test_find_first_assignable_task_skips_non_assignable(
    task_service, mock_redis_client
):
    """is_assignable()がFalseを返すIssueをスキップすることをテストします。"""
    # Arrange
    issue_not_assignable = create_mock_issue(
        number=1,
        title="Not Assignable",
        body="No deliverables section",
        labels=["BACKENDCODER", "P1"],
        has_branch_name=True,
    )
    issue_assignable = create_mock_issue(
        number=2,
        title="Assignable",
        body="""## 成果物\n- work""",
        labels=["BACKENDCODER", "P1"],
    )
    candidate_issues = [issue_not_assignable, issue_assignable]
    mock_redis_client.acquire_lock.return_value = True

    # Act
    result = await task_service._find_first_assignable_task(
        candidate_issues, "test-agent"
    )

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_2", "test-agent", timeout=600
    )


@pytest.mark.unit
@pytest.mark.anyio
async def test_find_first_assignable_task_skips_no_branch_name(
    task_service, mock_redis_client
):
    """ブランチ名が本文にないIssueをスキップすることをテストします。"""
    # Arrange
    issue_no_branch = create_mock_issue(
        number=1,
        title="No Branch",
        body="""## 成果物\n- work""",
        labels=["BACKENDCODER", "P1"],
        has_branch_name=False,
    )
    issue_with_branch = create_mock_issue(
        number=2,
        title="With Branch",
        body="""## 成果物\n- work""",
        labels=["BACKENDCODER", "P1"],
        has_branch_name=True,
    )
    candidate_issues = [issue_no_branch, issue_with_branch]
    mock_redis_client.acquire_lock.return_value = True

    # Act
    result = await task_service._find_first_assignable_task(
        candidate_issues, "test-agent"
    )

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_2", "test-agent", timeout=600
    )


@pytest.mark.unit
@pytest.mark.anyio
async def test_find_first_assignable_task_skips_locked_issue(
    task_service, mock_redis_client
):
    """RedisでロックされているIssueをスキップすることをテストします。"""
    # Arrange
    agent_id = "test-agent"
    issue_locked = create_mock_issue(
        number=1,
        title="Locked Issue",
        body="""## 成果物\n- work""",
        labels=["BACKENDCODER", "P1"],
    )
    issue_unlocked = create_mock_issue(
        number=2,
        title="Unlocked Issue",
        body="""## 成果物\n- work""",
        labels=["BACKENDCODER", "P1"],
    )
    candidate_issues = [issue_locked, issue_unlocked]
    mock_redis_client.acquire_lock.side_effect = [False, True]

    # Act
    result = await task_service._find_first_assignable_task(candidate_issues, agent_id)

    # Assert
    assert result is not None
    assert result.issue_id == 2
    assert mock_redis_client.acquire_lock.call_count == 2
    mock_redis_client.acquire_lock.assert_any_call(
        f"issue_lock_{issue_locked['number']}", agent_id, timeout=600
    )
    mock_redis_client.acquire_lock.assert_any_call(
        f"issue_lock_{issue_unlocked['number']}", agent_id, timeout=600
    )


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_selects_issue_with_any_role_label(
    task_service, mock_redis_client, mock_github_client
):
    """Issueに役割ラベルがあれば、エージェントの役割に関係なく選択されることをテストします。"""
    # Arrange
    issue_other_role = create_mock_issue(
        number=1,
        title="Other Role Task",
        body="""## 成果物\n- work""",
        labels=["BACKENDCODER", "P1"],
    )
    cached_issues = [issue_other_role]
    issue_keys = [
        f"repo::owner::repo:issue:{issue['number']}" for issue in cached_issues
    ]
    mock_redis_client.get_keys_by_pattern.return_value = issue_keys
    mock_redis_client.get_values.return_value = [
        json.dumps(issue) for issue in cached_issues
    ]
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    # Act
    result = await task_service.request_task(agent_id="test-agent")

    # Assert
    assert result is not None
    assert result.issue_id == 1
    assert result.required_role == "BACKENDCODER"


@pytest.mark.parametrize(
    "exception_to_raise, expected_log_message",
    [
        (
            GithubException(status=500, data="Server Error"),
            "Failed to update issue",
        ),
        (Exception("Unexpected error"), "An unexpected error occurred"),
    ],
)
@pytest.mark.unit
def test_complete_previous_task_handles_exceptions(
    exception_to_raise,
    expected_log_message,
    task_service,
    mock_redis_client,
    mock_github_client,
    caplog,
):
    """complete_previous_taskが例外を適切に処理することをテストします。"""
    # Arrange
    prev_issue_1 = create_mock_issue(
        number=101,
        title="Previous Task 1",
        body="",
        labels=["in-progress", "test-agent", "P1"],
    )
    prev_issue_2 = create_mock_issue(
        number=102,
        title="Previous Task 2",
        body="",
        labels=["in-progress", "test-agent", "P1"],
    )
    mock_github_client.find_issues_by_labels.return_value = [prev_issue_1, prev_issue_2]
    agent_id = "test-agent"

    mock_github_client.update_issue.side_effect = [
        exception_to_raise,
        None,
    ]

    with caplog.at_level(logging.ERROR):
        # Act
        task_service.complete_previous_task(agent_id)

        # Assert
        assert mock_github_client.update_issue.call_count == 2
        assert expected_log_message in caplog.text
        mock_github_client.update_issue.assert_called_with(
            issue_id=prev_issue_2["number"],
            remove_labels=["in-progress", agent_id],
            add_labels=["needs-review"],
        )


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_stores_current_task_in_redis(
    task_service, mock_redis_client, mock_github_client
):
    """タスク割り当て時にRedisに現在のタスクIDを保存することをテストします。"""
    # Arrange
    agent_id = "test-agent"
    agent_role = "BACKENDCODER"
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""## 成果物\n- test.py""",
        labels=[agent_role, "P1"],
    )
    cached_issues = [issue]
    issue_keys = [
        f"repo::owner::repo:issue:{issue['number']}" for issue in cached_issues
    ]
    mock_redis_client.get_keys_by_pattern.return_value = issue_keys
    mock_redis_client.get_values.return_value = [
        json.dumps(issue) for issue in cached_issues
    ]
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    # Act
    await task_service.request_task(agent_id=agent_id)

    # Assert
    mock_redis_client.set_value.assert_called_once_with(
        f"agent_current_task:{agent_id}", str(issue["number"]), timeout=3600
    )


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_sets_task_type_to_review_for_needs_review_issue(
    task_service, mock_redis_client, mock_github_client
):
    """'needs-review'ラベルを持つIssueが割り当てられた際に、task_typeが'review'に設定されることをテストします。"""
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Review Task",
        body="""## 成果物\n- review.py""",
        labels=["BACKENDCODER", "needs-review"],
    )
    cached_issues = [issue]
    issue_keys = [
        f"repo::owner::repo:issue:{issue['number']}" for issue in cached_issues
    ]
    mock_redis_client.get_keys_by_pattern.return_value = issue_keys
    mock_redis_client.get_values.return_value = [
        json.dumps(issue) for issue in cached_issues
    ]
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True
    # Set the timestamp to be older than the delay
    old_timestamp = datetime.now(UTC) - timedelta(
        minutes=task_service.REVIEW_ASSIGNMENT_DELAY_MINUTES + 1
    )
    mock_redis_client.get_value.return_value = old_timestamp.isoformat()

    agent_id = "test-agent"

    # Act
    result = await task_service.request_task(agent_id=agent_id)

    # Assert
    assert result is not None
    assert result.required_role == "BACKENDCODER"
    assert result.issue_id == 1
    assert result.task_type == TaskType.REVIEW
    mock_redis_client.get_keys_by_pattern.assert_called_once_with("issue:*")
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_1", agent_id, timeout=600
    )
    task_service.gemini_executor.build_prompt.assert_called_once_with(
        html_url=issue["html_url"],
        branch_name="feature/issue-1",
    )
    mock_redis_client.set_value.assert_called_once_with(
        f"agent_current_task:{agent_id}", str(issue["number"]), timeout=3600
    )


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_calls_gemini_executor_execute(
    task_service, mock_redis_client, mock_github_client
):
    """request_taskがGeminiExecutorのexecuteメソッドを呼び出すことをテストします。"""
    # Arrange
    agent_id = "test-agent"
    agent_role = "BACKENDCODER"
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""## 成果物\n- test.py""",
        labels=[agent_role, "P1"],
    )
    cached_issues = [issue]
    issue_keys = [
        f"repo::owner::repo:issue:{issue['number']}" for issue in cached_issues
    ]
    mock_redis_client.get_keys_by_pattern.return_value = issue_keys
    mock_redis_client.get_values.return_value = [
        json.dumps(issue) for issue in cached_issues
    ]
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    # GeminiExecutorのexecuteメソッドのモックを設定
    task_service.gemini_executor.execute.return_value = "Gemini Executor Output"

    # Act
    result = await task_service.request_task(agent_id=agent_id)

    # Assert
    assert result is not None
    task_service.gemini_executor.execute.assert_called_once_with(
        issue_id=issue["number"],
        html_url=issue["html_url"],
        branch_name="feature/issue-1",
        prompt="Generated Prompt",
    )
    assert result.gemini_response == "Gemini Executor Output"


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_complete_previous_task_finds_and_completes_issues_via_github_api(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """complete_previous_taskがGitHub APIから直接Issueを検索して完了処理を行うことをテストします。"""
    # Arrange
    agent_id = "test-agent"
    previous_issue = create_mock_issue(
        number=101,
        title="Previous Task",
        body="",
        labels=["in-progress", agent_id, "P1"],
    )
    mock_github_client.find_issues_by_labels.return_value = [previous_issue]

    # Act
    task_service.complete_previous_task(agent_id)

    # Assert
    mock_github_client.find_issues_by_labels.assert_called_once_with(
        labels=["in-progress", agent_id]
    )
    mock_github_client.update_issue.assert_called_once_with(
        issue_id=previous_issue["number"],
        remove_labels=["in-progress", agent_id],
        add_labels=["needs-review"],
    )


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_complete_previous_task_no_issues_found_via_github_api(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """
    GitHub API経由でin-progressのIssueが見つからない場合に、何も処理しないことをテストします。
    """
    # Arrange
    agent_id = "test-agent"
    mock_github_client.find_issues_by_labels.return_value = []

    # Act
    task_service.complete_previous_task(agent_id)

    # Assert
    mock_github_client.find_issues_by_labels.assert_called_once_with(
        labels=["in-progress", agent_id]
    )
    # 更新処理は呼び出されないことを確認
    mock_github_client.update_issue.assert_not_called()


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_complete_previous_task_handles_multiple_issues(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """
    複数のin-progressのIssueが見つかった場合に、すべて完了処理を行うことをテストします。
    """
    # Arrange
    agent_id = "test-agent"
    previous_issue_1 = create_mock_issue(
        number=101,
        title="Previous Task 1",
        body="",
        labels=["in-progress", agent_id, "P1"],
    )
    previous_issue_2 = create_mock_issue(
        number=102,
        title="Previous Task 2",
        body="",
        labels=["in-progress", agent_id, "P1"],
    )
    mock_github_client.find_issues_by_labels.return_value = [
        previous_issue_1,
        previous_issue_2,
    ]

    # Act
    task_service.complete_previous_task(agent_id)

    # Assert
    mock_github_client.find_issues_by_labels.assert_called_once_with(
        labels=["in-progress", agent_id]
    )
    # 両方のIssueが更新されることを確認
    assert mock_github_client.update_issue.call_count == 2
    mock_github_client.update_issue.assert_any_call(
        issue_id=previous_issue_1["number"],
        remove_labels=["in-progress", agent_id],
        add_labels=["needs-review"],
    )
    mock_github_client.update_issue.assert_any_call(
        issue_id=previous_issue_2["number"],
        remove_labels=["in-progress", agent_id],
        add_labels=["needs-review"],
    )


@pytest.mark.parametrize(
    "exception_to_raise, expected_log_message",
    [
        (
            GithubException(status=500, data="Server Error"),
            "Failed to update issue",
        ),
        (Exception("Unexpected error"), "An unexpected error occurred"),
    ],
)
@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_complete_previous_task_handles_github_exception(
    mock_sleep,
    task_service,
    mock_redis_client,
    mock_github_client,
    caplog,
    exception_to_raise,
    expected_log_message,
):
    """
    complete_previous_task内でGitHub APIの例外が発生した場合の処理をテストします。
    """
    # Arrange
    agent_id = "test-agent"
    previous_issue = create_mock_issue(
        number=101,
        title="Previous Task",
        body="",
        labels=["in-progress", agent_id, "P1"],
    )
    mock_github_client.find_issues_by_labels.return_value = [previous_issue]
    mock_github_client.update_issue.side_effect = GithubException(
        status=500, data="GitHub API Error"
    )

    with caplog.at_level(logging.ERROR):
        # Act
        task_service.complete_previous_task(agent_id)

        # Assert
        mock_github_client.find_issues_by_labels.assert_called_once_with(
            labels=["in-progress", agent_id]
        )
        mock_github_client.update_issue.assert_called_once_with(
            issue_id=previous_issue["number"],
            remove_labels=["in-progress", agent_id],
            add_labels=["needs-review"],
        )
        # エラーログが記録されることを確認
        assert (
            f"[issue_id={previous_issue['number']}, agent_id={agent_id}] Failed to update issue"
            in caplog.text
        )


@pytest.mark.unit
def test_sort_issues_by_priority(task_service):
    """Issueが優先度ラベルに基づいて正しくソートされることをテストします。"""
    # Arrange
    issue_p1 = create_mock_issue(
        number=1, title="P1 Task", body="", labels=["P1", "feature"]
    )
    issue_p0 = create_mock_issue(
        number=2, title="P0 Task", body="", labels=["P0", "bug"]
    )
    issue_no_priority = create_mock_issue(
        number=3, title="No Priority Task", body="", labels=["documentation"]
    )
    issue_p2 = create_mock_issue(number=4, title="P2 Task", body="", labels=["P2"])
    issue_p0_another = create_mock_issue(
        number=5, title="Another P0 Task", body="", labels=["P0"]
    )

    issues = [issue_p1, issue_p0, issue_no_priority, issue_p2, issue_p0_another]

    # Act
    sorted_issues = task_service._sort_issues_by_priority(issues)

    # Assert
    # 期待されるソート順: P0, P0, P1, P2, No Priority
    expected_order = [
        issue_p0["number"],
        issue_p0_another["number"],
        issue_p1["number"],
        issue_p2["number"],
        issue_no_priority["number"],
    ]
    actual_order = [issue["number"] for issue in sorted_issues]
    assert actual_order == expected_order


@pytest.mark.unit
def test_filter_by_highest_priority(task_service):
    """Issueリストが最高優先度ラベルに基づいて正しくフィルタリングされることをテストします。"""
    # Arrange
    highest_priority_label = "P1"
    issue_p1_a = create_mock_issue(
        number=1, title="P1 Task A", body="", labels=["P1", "feature"]
    )
    issue_p1_b = create_mock_issue(
        number=2, title="P1 Task B", body="", labels=["P1", "bug"]
    )
    issue_p0 = create_mock_issue(
        number=3, title="P0 Task", body="", labels=["P0", "bug"]
    )
    issue_p2 = create_mock_issue(
        number=4, title="P2 Task", body="", labels=["P2", "documentation"]
    )
    issue_no_priority = create_mock_issue(
        number=5, title="No Priority Task", body="", labels=["documentation"]
    )

    issues = [issue_p1_a, issue_p1_b, issue_p0, issue_p2, issue_no_priority]

    # Act
    filtered_issues = task_service._filter_by_highest_priority(
        issues, highest_priority_label
    )

    # Assert
    expected_numbers = {1, 2}
    actual_numbers = {issue["number"] for issue in filtered_issues}
    assert actual_numbers == expected_numbers
    assert len(filtered_issues) == 2


@pytest.mark.unit
def test_find_candidates_for_any_role_filters_no_priority(task_service):
    """_find_candidates_for_any_roleが優先度ラベルのないIssueを除外することをテストします。"""
    # Arrange
    issue_with_priority = create_mock_issue(
        number=1, title="With Priority", body="", labels=["BACKENDCODER", "P1"]
    )
    issue_without_priority = create_mock_issue(
        number=2, title="No Priority", body="", labels=["BACKENDCODER"]
    )
    issues = [issue_with_priority, issue_without_priority]

    # Act
    candidates = task_service._find_candidates_for_any_role(issues)

    # Assert
    assert len(candidates) == 1
    assert candidates[0]["number"] == issue_with_priority["number"]


@pytest.mark.parametrize(
    "case, labels",
    [
        ("development", ["BACKENDCODER", "P1"]),
        ("review", ["BACKENDCODER", "needs-review"]),
    ],
)
def test_find_candidates_for_any_role_filters_story_and_epic_labels(
    task_service, mock_redis_client, case, labels
):
    """_find_candidates_for_any_roleが'story'または'epic'ラベルを持つIssueを除外することをテストします。"""
    # Arrange
    issue_story = create_mock_issue(
        number=1, title="Story Issue", body="", labels=labels + ["story"]
    )
    issue_epic = create_mock_issue(
        number=2, title="Epic Issue", body="", labels=labels + ["epic"]
    )
    issue_task = create_mock_issue(number=3, title="Task Issue", body="", labels=labels)
    issues = [issue_story, issue_epic, issue_task]

    if case == "review":
        mock_redis_client.get_value.return_value = None

    # Act
    candidates = task_service._find_candidates_for_any_role(issues)

    # Assert
    if case == "review":
        assert len(candidates) == 0
    else:
        assert len(candidates) == 1
        assert candidates[0]["number"] == issue_task["number"]


@pytest.mark.unit
def test_create_task_candidate_stores_in_redis(task_service, mock_redis_client):
    """create_task_candidateがTaskCandidateをRedisに正しく保存することをテストします。"""
    # Arrange
    issue_id = 123
    agent_id = "test-agent"

    # Act
    task_service.create_task_candidate(issue_id, agent_id)

    # Assert
    mock_redis_client.set_value.assert_called_once()
    call_args, call_kwargs = mock_redis_client.set_value.call_args
    assert call_args[0] == f"task_candidate:{issue_id}:{agent_id}"
    stored_value = json.loads(call_args[1])
    assert stored_value["issue_id"] == issue_id
    assert stored_value["agent_id"] == agent_id
    assert stored_value["status"] == "pending"


@pytest.mark.unit
def test_poll_and_process_reviews_uses_is_open_query(task_service, mock_github_client):
    """
    poll_and_process_reviewsがneeds-reviewのIssueを検索する際に、
    is:open条件を明示的に使用することをテストします。
    """
    # Arrange
    mock_github_client.get_needs_review_issues_and_prs.return_value = {}

    # Act
    task_service.poll_and_process_reviews()

    # Assert
    mock_github_client.get_needs_review_issues_and_prs.assert_called_once_with()


@pytest.mark.unit
def test_poll_and_process_reviews_adds_label_after_timeout(
    task_service, mock_github_client
):
    """
    ポーリングサービスが、タイムアウトしたレビュー待ちPRに 'review-done' ラベルを付与することをテストします。
    """
    # Arrange
    pr_number = 123
    now = datetime.now(UTC)
    pr_created_time = now - timedelta(
        minutes=task_service.settings.REVIEW_TIMEOUT_MINUTES + 1
    )
    mock_pr = create_mock_pr(number=pr_number, created_at=pr_created_time)

    # 新しいメソッドのモック設定
    mock_github_client.get_needs_review_issues_and_prs.return_value = {
        pr_number: mock_pr
    }

    # Act
    task_service.poll_and_process_reviews()

    # Assert
    mock_github_client.get_needs_review_issues_and_prs.assert_called_once()
    mock_github_client.add_label_to_pr.assert_called_once_with(
        pr_number=pr_number, label=task_service.LABEL_REVIEW_DONE
    )


@pytest.mark.unit
@pytest.mark.anyio
async def test_create_fix_task_creates_task_and_builds_prompt(task_service):
    """create_fix_taskがプロンプトを生成し、FIXタスクをRedisに保存することをテストします。"""
    # Arrange
    pull_request_number = 123
    review_comments = ["Your code needs fixing."]
    pr_url = f"https://github.com/test/repo/pull/{pull_request_number}"
    generated_prompt = (
        f"Please fix the code based on the following comments: {review_comments}"
    )
    task_service.gemini_executor.build_code_review_prompt.return_value = (
        generated_prompt
    )

    # Act
    await task_service.create_fix_task(pull_request_number, review_comments)

    # Assert
    task_service.gemini_executor.build_code_review_prompt.assert_called_once_with(
        pr_url=pr_url, review_comments=review_comments
    )

    task_service.redis_client.set_value.assert_called_once()
    call_args, _ = task_service.redis_client.set_value.call_args
    redis_key = call_args[0]
    redis_value = json.loads(call_args[1])

    assert redis_key == f"task:fix:{pull_request_number}"
    assert redis_value["task_type"] == TaskType.FIX.value
    assert redis_value["title"] == f"Fix task for PR #{pull_request_number}"
    assert redis_value["body"] == generated_prompt
    assert redis_value["issue_id"] == pull_request_number


@pytest.mark.unit
def test_find_candidates_for_any_role_review_candidate_with_review_done_pr(
    task_service, mock_github_client, mock_redis_client
):
    """
    _find_candidates_for_any_roleが、needs-reviewラベルとreview-doneラベルを持つPRを持つIssueを
    レビュー候補として正しく選択することをテストします。
    """
    # Arrange
    issue_review = create_mock_issue(
        number=1,
        title="Review Task",
        body="",
        labels=["BACKENDCODER", task_service.LABEL_NEEDS_REVIEW],
    )
    issues = [issue_review]

    old_timestamp = datetime.now(UTC) - timedelta(
        minutes=task_service.REVIEW_ASSIGNMENT_DELAY_MINUTES + 1
    )
    mock_redis_client.get_value.return_value = old_timestamp.isoformat()

    # Act
    candidates = task_service._find_candidates_for_any_role(issues)

    # Assert
    assert len(candidates) == 1
    assert candidates[0]["number"] == issue_review["number"]


@pytest.mark.unit
def test_find_candidates_for_any_role_review_candidate_without_review_done_pr(
    task_service, mock_github_client, mock_redis_client
):
    """
    _find_candidates_for_any_roleが、needs-reviewラベルを持つがreview-doneラベルがないPRを持つIssueを
    レビュー候補として選択しないことをテストします。
    """
    # Arrange
    issue_review = create_mock_issue(
        number=1,
        title="Review Task",
        body="",
        labels=["BACKENDCODER", task_service.LABEL_NEEDS_REVIEW],
    )
    issues = [issue_review]

    mock_redis_client.get_value.return_value = None

    # Act
    candidates = task_service._find_candidates_for_any_role(issues)

    # Assert
    assert len(candidates) == 0


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_logs_detailed_information(
    task_service, mock_redis_client, mock_github_client, caplog
):
    """タスク割り当てプロセス中に詳細なログが出力されることをテストします。"""
    # Arrange
    agent_id = "test-agent-for-logging"
    issue_not_assignable = create_mock_issue(
        number=3,
        title="Not Assignable",
        body="No deliverables section",
        labels=["BACKENDCODER", "P0"],
        has_branch_name=True,
    )
    issue_no_branch = create_mock_issue(
        number=2,
        title="No Branch",
        body="""## 成果物\n- work""",
        labels=["BACKENDCODER", "P1"],
        has_branch_name=False,
    )
    issue_locked = create_mock_issue(
        number=1,
        title="Locked Issue",
        body="""## 成果物\n- work""",
        labels=["BACKENDCODER", "P2"],
    )
    issue_assignable = create_mock_issue(
        number=4,
        title="Assignable Task",
        body="""## 成果物\n- work""",
        labels=["BACKENDCODER", "P3"],
    )

    cached_issues = [
        issue_locked,
        issue_no_branch,
        issue_not_assignable,
        issue_assignable,
    ]
    issue_keys = [f"issue:{issue['number']}" for issue in cached_issues]
    mock_redis_client.get_keys_by_pattern.return_value = issue_keys
    mock_redis_client.get_values.return_value = [
        json.dumps(issue) for issue in cached_issues
    ]
    mock_github_client.find_issues_by_labels.return_value = []

    def acquire_lock_side_effect(key, *args, **kwargs):
        return "issue_lock_1" not in key

    mock_redis_client.acquire_lock.side_effect = acquire_lock_side_effect

    with caplog.at_level(logging.INFO):
        # Act
        result = await task_service.request_task(agent_id=agent_id)

        # Assert
        assert result is not None
        assert result.issue_id == 4

        log_messages = [record.message for record in caplog.records]

        # 1. Agent ID
        assert f"タスクをリクエストしています: agent_id={agent_id}" in log_messages
        # 2. Candidate count
        assert "役割に紐づく候補Issueが4件見つかりました。" in log_messages
        # 3. Sorted order
        assert "候補Issueを優先度順にソートしました: [3, 2, 1, 4]" in log_messages
        # 4. Reasons for skipping
        assert any(
            "Issueは割り当て不可能です" in m and "issue_id=3" in m for m in log_messages
        )
        assert any(
            "ブランチ名が見つかりません" in m and "issue_id=2" in m
            for m in log_messages
        )
        assert any(
            "Issue is locked by another agent" in m and "issue_id=1" in m
            for m in log_messages
        )
        # 5. Successful assignment
        assert any(
            "Lock acquired for issue" in m
            and "issue_id=4" in m
            and f"agent_id={agent_id}" in m
            for m in log_messages
        )


@pytest.mark.unit
def test_find_candidates_for_any_role_review_candidate_no_pr_found(
    task_service, mock_github_client, mock_redis_client
):
    """
    _find_candidates_for_any_roleが、needs-reviewラベルを持つが関連するPRが見つからないIssueを
    レビュー候補として選択しないことをテストします。
    """
    # Arrange
    issue_review = create_mock_issue(
        number=1,
        title="Review Task",
        body="",
        labels=["BACKENDCODER", task_service.LABEL_NEEDS_REVIEW],
    )
    issues = [issue_review]

    mock_redis_client.get_value.return_value = None

    # Act
    candidates = task_service._find_candidates_for_any_role(issues)

    # Assert
    assert len(candidates) == 0


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_returns_none_immediately_if_no_task_available(
    task_service, mock_redis_client, mock_github_client
):
    """
    タスクがロックされている場合に、request_taskが即座にNoneを返すことをテストします。
    """
    # Arrange
    issue = create_mock_issue(1, "test_title", "test_body", ["BACKENDCODER", "P1"])
    mock_redis_client.get_keys_by_pattern.return_value = ["issue:1"]
    mock_redis_client.get_values.return_value = [json.dumps(issue)]
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = False  # Make the issue locked
    agent_id = "test-agent"

    # Act
    result = await task_service.request_task(agent_id=agent_id)

    # Assert
    assert result is None
    mock_github_client.find_issues_by_labels.assert_called_once_with(
        labels=["in-progress", agent_id]
    )
    mock_redis_client.get_keys_by_pattern.assert_called_once_with("issue:*")
