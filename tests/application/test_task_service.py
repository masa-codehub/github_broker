import json
import logging
import threading
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from github import GithubException

from github_broker.application.task_service import OPEN_ISSUES_CACHE_KEY, TaskService
from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor


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

    mock_gemini_executor_instance = MagicMock(spec=GeminiExecutor)
    mock_gemini_executor_instance.build_prompt.return_value = (
        "Generated Prompt for Issue 2"
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
@pytest.mark.anyio
async def test_request_task_selects_by_role_from_cache(
    task_service, mock_redis_client, mock_github_client
):
    """Redisキャッシュから役割に合うIssueを正しく選択できることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1, title="Docs", body="", labels=["documentation"]
    )
    issue2 = create_mock_issue(
        number=2,
        title="Backend Task",
        body="""## 成果物
- test.py""",
        labels=["feature", "BACKENDCODER"],
    )
    cached_issues = [issue1, issue2]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    agent_id = "test-agent"
    agent_role = "BACKENDCODER"

    # Act
    result = await task_service.request_task(
        agent_id=agent_id, agent_role=agent_role, timeout=0
    )

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.get_value.assert_called_once_with(OPEN_ISSUES_CACHE_KEY)
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
async def test_request_task_no_matching_issue(
    task_service, mock_redis_client, mock_github_client
):
    """エージェントの役割に一致するIssueがない場合にNoneが返されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1,
        title="Docs",
        body="""## 成果物
- docs""",
        labels=["documentation"],
    )
    cached_issues = [issue1]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []
    agent_id = "test-agent"
    agent_role = "BACKENDCODER"

    # Act
    result = await task_service.request_task(
        agent_id=agent_id, agent_role=agent_role, timeout=0
    )

    # Assert
    assert result is None
    mock_redis_client.get_value.assert_called_once_with(OPEN_ISSUES_CACHE_KEY)


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_excludes_needs_review_label(
    task_service, mock_redis_client, mock_github_client
):
    """'needs-review'ラベルを持つIssueがタスク割り当てから除外されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1,
        title="Task Needs Review",
        body="""## 成果物
- review.py""",
        labels=["BACKENDCODER", "needs-review"],
    )
    issue2 = create_mock_issue(
        number=2,
        title="Assignable Task",
        body="""## 成果物
- assign.py""",
        labels=["BACKENDCODER"],
    )
    cached_issues = [issue1, issue2]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    # Act
    result = await task_service.request_task(
        agent_id="test-agent", agent_role="BACKENDCODER", timeout=0
    )

    # Assert
    assert result is not None
    assert result.issue_id == 2


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_completes_previous_task(
    task_service, mock_redis_client, mock_github_client
):
    """request_taskが前タスクの完了処理を呼び出すことをテストします。"""
    # Arrange
    agent_id = "test-agent"
    agent_role = "BACKENDCODER"
    prev_issue = create_mock_issue(
        number=1,
        title="Previous Task",
        body="",
        labels=["in-progress", agent_id],
    )
    new_issue = create_mock_issue(
        number=2,
        title="New Task",
        body="""## 成果物
- new.py""",
        labels=["BACKENDCODER"],
    )
    cached_issues = [new_issue]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_redis_client.acquire_lock.return_value = True

    # Setup GitHub API to return previous issue for completion
    mock_github_client.find_issues_by_labels.return_value = [prev_issue]

    # Act
    result = await task_service.request_task(
        agent_id=agent_id, agent_role=agent_role, timeout=0
    )

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
def test_find_first_assignable_task_exception_releases_lock(
    task_service, mock_github_client, mock_redis_client
):
    """
    _find_first_assignable_task内で例外が発生した場合にロックが解放されることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""## 成果物
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
def test_find_first_assignable_task_create_branch_exception_releases_lock(
    task_service, mock_github_client, mock_redis_client
):
    """
    _find_first_assignable_task内でcreate_branchが例外を発生させた場合にロックが解放されることをテストします。
    """
    # Arrange
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="""## 成果物
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
def test_find_first_assignable_task_rollback_labels_on_branch_creation_failure(
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
        body="""## 成果物
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
        mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")
        mock_github_client.update_issue.assert_called_once_with(
            issue_id=issue["number"], remove_labels=["in-progress", agent_id]
        )
        mock_github_client.remove_label.assert_not_called()


@pytest.mark.unit
def test_find_first_assignable_task_rollback_failure_logs_error(
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
        body="""## 成果物
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
        with pytest.raises(GithubException, match="Branch already exists"):
            task_service._find_first_assignable_task(candidate_issues, agent_id)

        assert "Failed to rollback labels" in caplog.text
        mock_redis_client.release_lock.assert_called_once_with("issue_lock_1")
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
        number=2,
        title="Assignable",
        body="""## 成果物
- work""",
        labels=["BACKENDCODER"],
    )
    candidate_issues = [issue_not_assignable, issue_assignable]
    mock_redis_client.acquire_lock.return_value = True

    # Act
    result = task_service._find_first_assignable_task(candidate_issues, "test-agent")

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_2", "test-agent", timeout=600
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
        body="""## 成果物
- work""",
        labels=["BACKENDCODER"],
        has_branch_name=False,
    )
    issue_with_branch = create_mock_issue(
        number=2,
        title="With Branch",
        body="""## 成果物
- work""",
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
        "issue_lock_2", "test-agent", timeout=600
    )


@pytest.mark.unit
def test_find_first_assignable_task_skips_locked_issue(task_service, mock_redis_client):
    """RedisでロックされているIssueをスキップすることをテストします。"""
    # Arrange
    agent_id = "test-agent"
    issue_locked = create_mock_issue(
        number=1,
        title="Locked Issue",
        body="""## 成果物
- work""",
        labels=["BACKENDCODER"],
    )
    issue_unlocked = create_mock_issue(
        number=2,
        title="Unlocked Issue",
        body="""## 成果物
- work""",
        labels=["BACKENDCODER"],
    )
    candidate_issues = [issue_locked, issue_unlocked]
    mock_redis_client.acquire_lock.side_effect = [False, True]

    # Act
    result = task_service._find_first_assignable_task(candidate_issues, agent_id)

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
async def test_no_matching_role_candidates(
    task_service, mock_redis_client, mock_github_client
):
    """オープンなIssueはあるが、役割に合う候補がない場合のテスト。"""
    # Arrange
    issue_other_role = create_mock_issue(
        number=1,
        title="Other Role Task",
        body="""## 成果物
- work""",
        labels=["FRONTENDCODER"],
    )
    cached_issues = [issue_other_role]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []

    # Act
    result = await task_service.request_task(
        agent_id="test-agent", agent_role="BACKENDCODER", timeout=0
    )

    # Assert
    assert result is None


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
        labels=["in-progress", "test-agent"],
    )
    prev_issue_2 = create_mock_issue(
        number=102,
        title="Previous Task 2",
        body="",
        labels=["in-progress", "test-agent"],
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
        body="""## 成果物
- test.py""",
        labels=[agent_role],
    )
    mock_redis_client.get_value.return_value = json.dumps([issue])
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    # Act
    await task_service.request_task(agent_id=agent_id, agent_role=agent_role, timeout=0)

    # Assert
    mock_redis_client.set_value.assert_called_once_with(
        f"agent_current_task:{agent_id}", str(issue["number"]), timeout=3600
    )


@pytest.mark.unit
@pytest.mark.anyio
@patch("asyncio.sleep", new_callable=AsyncMock)
@patch("time.monotonic")
async def test_request_task_long_polling_timeout(
    mock_time, mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """ロングポーリングがタイムアウト時間に達した場合にNoneを返すことをテストします。"""
    # Arrange
    mock_redis_client.get_value.return_value = json.dumps([])
    mock_github_client.find_issues_by_labels.return_value = []
    mock_time.side_effect = [0, 6, 12, 16]

    agent_id = "test-agent"
    agent_role = "BACKENDCODER"
    timeout = 15

    # Act
    result = await task_service.request_task(
        agent_id=agent_id, agent_role=agent_role, timeout=timeout
    )

    # Assert
    assert result is None
    assert mock_sleep.call_count == 2


@pytest.mark.unit
@pytest.mark.anyio
@patch("asyncio.sleep", new_callable=AsyncMock)
@patch("time.monotonic")
async def test_request_task_long_polling_finds_task_during_wait(
    mock_time, mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """ロングポーリング中にタスクが見つかった場合に即座に返すことをテストします。"""
    # Arrange
    issue = create_mock_issue(
        number=123,
        title="Found Task",
        body="""## 成果物
- found.py""",
        labels=["BACKENDCODER"],
    )

    mock_redis_client.get_value.side_effect = [
        json.dumps([]),
        json.dumps([issue]),
    ]
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    mock_time.side_effect = [0, 6]

    agent_id = "test-agent"
    agent_role = "BACKENDCODER"
    timeout = 30

    # Act
    result = await task_service.request_task(
        agent_id=agent_id, agent_role=agent_role, timeout=timeout
    )

    # Assert
    assert result is not None
    assert result.issue_id == 123
    mock_sleep.assert_called_once()


@pytest.mark.unit
@pytest.mark.anyio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_request_task_no_timeout_returns_immediately(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """timeout=Noneの場合に即座にNoneを返すことをテストします。"""
    # Arrange
    cached_issues = []
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []

    agent_id = "test-agent"
    agent_role = "BACKENDCODER"

    # Act
    result = await task_service.request_task(
        agent_id=agent_id, agent_role=agent_role, timeout=None
    )

    # Assert
    assert result is None
    mock_sleep.assert_not_called()


@pytest.mark.unit
@pytest.mark.anyio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_request_task_finds_task_immediately_no_polling(
    mock_sleep, task_service, mock_redis_client, mock_github_client
):
    """最初のチェックでタスクが見つかった場合にポーリングせずに即座に返すことをテストします。"""
    # Arrange
    issue = create_mock_issue(
        number=456,
        title="Immediate Task",
        body="""## 成果物
- immediate.py""",
        labels=["BACKENDCODER"],
    )
    cached_issues = [issue]
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    agent_id = "test-agent"
    agent_role = "BACKENDCODER"
    timeout = 30

    # Act
    result = await task_service.request_task(
        agent_id=agent_id, agent_role=agent_role, timeout=timeout
    )

    # Assert
    assert result is not None
    assert result.issue_id == 456
    mock_sleep.assert_not_called()


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
        labels=["in-progress", agent_id],
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
        labels=["in-progress", agent_id],
    )
    previous_issue_2 = create_mock_issue(
        number=102,
        title="Previous Task 2",
        body="",
        labels=["in-progress", agent_id],
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


@pytest.mark.unit
@patch("time.sleep", return_value=None)
def test_complete_previous_task_handles_github_exception(
    mock_sleep, task_service, mock_redis_client, mock_github_client, caplog
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
        labels=["in-progress", agent_id],
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
