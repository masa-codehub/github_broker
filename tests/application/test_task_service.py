import json
import logging
from unittest.mock import MagicMock, patch

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
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    agent_id = "test-agent"
    agent_role = "BACKENDCODER"

    # Act
    result = task_service.request_task(agent_id=agent_id, agent_role=agent_role)

    # Assert
    assert result is not None
    assert result.issue_id == 2
    mock_redis_client.get_value.assert_called_once_with(OPEN_ISSUES_CACHE_KEY)
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
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_github_client.find_issues_by_labels.return_value = []
    agent_id = "test-agent"
    agent_role = "BACKENDCODER"

    # Act
    result = task_service.request_task(agent_id=agent_id, agent_role=agent_role)

    # Assert
    assert result is None
    mock_redis_client.get_value.assert_called_once_with(OPEN_ISSUES_CACHE_KEY)


@pytest.mark.unit
def test_request_task_completes_previous_task(
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
        body="## 成果物\n- new.py",
        labels=["BACKENDCODER"],
    )
    cached_issues = [new_issue]  # Only new task in cache
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_redis_client.acquire_lock.return_value = True

    # Setup GitHub API to return previous issue for completion
    mock_github_client.find_issues_by_labels.return_value = [prev_issue]

    # Act
    result = task_service.request_task(agent_id=agent_id, agent_role=agent_role)

    # Assert
    # Check that find_issues_by_labels was called for completion
    mock_github_client.find_issues_by_labels.assert_called_once_with(
        labels=["in-progress", agent_id]
    )
    # Check that update_issue was called for the previous task completion
    update_calls = mock_github_client.update_issue.call_args_list
    assert len(update_calls) >= 1, "update_issue should be called at least once"
    # The first call should be for completing the previous task
    first_call = update_calls[0]
    assert first_call[1]["issue_id"] == prev_issue["number"]
    assert first_call[1]["remove_labels"] == ["in-progress", agent_id]
    assert first_call[1]["add_labels"] == ["needs-review"]

    assert result is not None
    assert result.issue_id == new_issue["number"]


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
    new_issue = create_mock_issue(
        number=201,
        title="New Task",
        body="## 成果物\n- new.py",
        labels=["BACKENDCODER"],
    )
    cached_issues = [new_issue]  # キャッシュには新しいタスクのみ
    mock_redis_client.get_value.return_value = json.dumps(cached_issues)
    mock_redis_client.acquire_lock.return_value = True

    # GitHub API呼び出しをセットアップ
    mock_github_client.find_issues_by_labels.return_value = [prev_issue_1, prev_issue_2]

    agent_id = "test-agent"
    agent_role = "BACKENDCODER"

    # 最初のupdate_issueで例外を発生させ、2番目は成功させる
    mock_github_client.update_issue.side_effect = [
        exception_to_raise,
        None,  # 2番目のcomplete_previous_task呼び出しは成功
        None,  # add_labelの呼び出し
        None,  # add_labelの呼び出し
    ]

    with caplog.at_level(logging.ERROR):
        # Act
        result = task_service.request_task(agent_id=agent_id, agent_role=agent_role)

        # Assert
        # find_issues_by_labelsが呼び出されたことを確認
        mock_github_client.find_issues_by_labels.assert_called_once_with(
            labels=["in-progress", agent_id]
        )
        # update_issueが複数回呼び出されたことを確認（complete_previous_task + add_labels）
        assert mock_github_client.update_issue.call_count >= 2
        # 最初のIssueでエラーがログに記録されたことを確認
        assert expected_log_message in caplog.text
        # 新しいタスクが正常に返されたことを確認
        assert result is not None
        assert result.issue_id == new_issue["number"]


@pytest.mark.unit
def test_request_task_stores_current_task_in_redis(
    task_service, mock_redis_client, mock_github_client
):
    """タスク割り当て時にRedisに現在のタスクIDを保存することをテストします。"""
    # Arrange
    agent_id = "test-agent"
    agent_role = "BACKENDCODER"
    issue = create_mock_issue(
        number=1,
        title="Test Task",
        body="## 成果物\n- test.py",
        labels=[agent_role],
    )
    mock_redis_client.get_value.return_value = json.dumps([issue])
    mock_github_client.find_issues_by_labels.return_value = []
    mock_redis_client.acquire_lock.return_value = True

    # Act
    task_service.request_task(agent_id=agent_id, agent_role=agent_role)

    # Assert
    mock_redis_client.set_value.assert_called_once_with(
        f"agent_current_task:{agent_id}", str(issue["number"]), timeout=3600
    )


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
