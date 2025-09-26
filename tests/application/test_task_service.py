import json
import logging
import threading
from unittest.mock import MagicMock, call, patch

import pytest

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
    with patch("time.sleep"):
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
    with patch("time.sleep"):
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
def test_request_task_selects_by_role_from_cache(
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
        body="## 成果物\n- test.py",
        labels=["feature", "BACKENDCODER"],
    )
    cached_issues = [issue1, issue2]
    mock_redis_client.get_value.side_effect = [json.dumps(cached_issues), None]
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    agent_id = "test-agent"
    agent_role = "BACKENDCODER"

    # Act
    result = task_service.request_task(agent_id=agent_id, agent_role=agent_role)

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.get_value.assert_has_calls(
        [call(OPEN_ISSUES_CACHE_KEY), call(f"agent_current_task:{agent_id}")]
    )
    mock_redis_client.acquire_lock.assert_called_once_with(
        "issue_lock_2", agent_id, timeout=600
    )
    task_service.gemini_executor.build_prompt.assert_called_once_with(
        issue_id=issue2["number"],
        title=issue2["title"],
        body=issue2["body"],
        branch_name="feature/issue-2",
    )
    mock_redis_client.set_value.assert_called_once_with(
        f"agent_current_task:{agent_id}", str(issue2["number"]), timeout=3600
    )


@pytest.mark.unit
def test_request_task_no_matching_issue(
    task_service, mock_redis_client, mock_github_client
):
    """エージェントの役割に一致するIssueがない場合にNoneが返されることをテストします。"""
    # Arrange
    issue1 = create_mock_issue(
        number=1, title="Docs", body="## 成果物\n- docs", labels=["documentation"]
    )
    cached_issues = [issue1]
    mock_redis_client.get_value.side_effect = [json.dumps(cached_issues), None]
    mock_github_client.find_issues_by_labels.return_value = []
    agent_id = "test-agent"
    agent_role = "BACKENDCODER"

    # Act
    result = task_service.request_task(agent_id=agent_id, agent_role=agent_role)

    # Assert
    assert result is None
    mock_redis_client.get_value.assert_has_calls(
        [call(OPEN_ISSUES_CACHE_KEY), call(f"agent_current_task:{agent_id}")]
    )


@pytest.mark.unit
def test_complete_previous_task_handles_invalid_redis_id(
    task_service, mock_redis_client, mock_github_client, caplog
):
    """Redisに保存されたIDが無効な場合にエラーを記録し、GitHub検索にフォールバックすることをテストします。"""
    # Arrange
    agent_id = "test-agent"
    mock_redis_client.get_value.return_value = "invalid-id"
    all_issues = []

    # Act
    with caplog.at_level(logging.ERROR):
        task_service.complete_previous_task(agent_id, all_issues)

    # Assert
    assert "Invalid issue ID 'invalid-id' stored in Redis" in caplog.text
    mock_github_client.find_issues_by_labels.assert_called_once_with(
        labels=["in-progress", agent_id]
    )


@pytest.mark.unit
def test_find_first_assignable_task_skips_locked_issue(task_service, mock_redis_client):
    """RedisでロックされているIssueをスキップすることをテストします。"""
    # Arrange
    agent_id = "test-agent"
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
