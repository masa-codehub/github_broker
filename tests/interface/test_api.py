import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

# DIコンテナをテストモードで読み込むために、最初に環境変数を設定
os.environ["TESTING"] = "true"

from broker_main import app
from github_broker.application.exceptions import LockAcquisitionError
from github_broker.application.task_service import TaskService
from github_broker.interface.api import get_task_service
from github_broker.interface.models import TaskResponse


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_task_service():
    """TaskServiceの依存関係をモックするためのフィクスチャ。"""
    mock_service = MagicMock(spec=TaskService)
    mock_service.request_task = AsyncMock()
    mock_service.create_fix_task = AsyncMock()
    app.dependency_overrides[get_task_service] = lambda: mock_service
    yield mock_service
    # ティアダウン：オーバーライドをクリーンアップ
    del app.dependency_overrides[get_task_service]


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_success(client, mock_task_service):
    """/request-taskエンドポイントへの成功したタスクリクエストをテストします。"""
    # Arrange
    expected_task = TaskResponse(
        issue_id=123,
        issue_url="http://example.com/issue/123",
        title="テストIssue",
        body="これはテストIssueです。",
        labels=["bug"],
        branch_name="feature/issue-123-test",
        prompt="これはテストプロンプトです。",
    )
    mock_task_service.request_task.return_value = expected_task
    request_body = {
        "agent_id": "test-agent",
        "agent_role": "BACKENDCODER",
        "timeout": 60,
    }

    # Act
    response = client.post("/request-task", json=request_body)

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_task.model_dump(mode="json")
    mock_task_service.request_task.assert_awaited_once_with(
        agent_id=request_body["agent_id"],
        agent_role=request_body["agent_role"],
        timeout=request_body["timeout"],
    )


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_no_task_available(client, mock_task_service):
    """利用可能なタスクがない場合（204 No Content）の/request-taskエンドポイントをテストします。"""
    # Arrange
    mock_task_service.request_task.return_value = None
    request_body = {
        "agent_id": "test-agent",
        "agent_role": "BACKENDCODER",
        "timeout": 10,
    }

    # Act
    response = client.post("/request-task", json=request_body)

    # Assert
    assert response.status_code == 204
    mock_task_service.request_task.assert_awaited_once_with(
        agent_id=request_body["agent_id"],
        agent_role=request_body["agent_role"],
        timeout=request_body["timeout"],
    )


@pytest.mark.unit
@pytest.mark.anyio
async def test_request_task_lock_error(client, mock_task_service):
    """LockAcquisitionErrorが発生した場合の/request-taskエンドポイントをテストします。"""
    # Arrange
    error_message = "サーバーがビジー状態です。後でもう一度お試しください。"
    mock_task_service.request_task.side_effect = LockAcquisitionError(error_message)
    request_body = {
        "agent_id": "test-agent",
        "agent_role": "BACKENDCODER",
    }

    # Act
    response = client.post("/request-task", json=request_body)

    # Assert
    assert response.status_code == 503
    assert response.json() == {"message": error_message}
    mock_task_service.request_task.assert_awaited_once_with(
        agent_id=request_body["agent_id"],
        agent_role=request_body["agent_role"],
        timeout=120,
    )


@pytest.mark.unit
@pytest.mark.anyio
async def test_create_fix_task_endpoint(client, mock_task_service):
    """/tasks/fixエンドポイントがTaskService.create_fix_taskを呼び出すことをテストします。"""
    # Arrange
    request_body = {
        "pull_request_number": 123,
        "review_comments": ["This needs a fix."],
    }
    mock_task_service.create_fix_task.return_value = None

    # Act
    response = client.post("/tasks/fix", json=request_body)

    # Assert
    assert response.status_code == 202
    assert response.json() == {"message": "Fix task creation has been accepted."}
    mock_task_service.create_fix_task.assert_awaited_once_with(
        pull_request_number=request_body["pull_request_number"],
        review_comments=request_body["review_comments"],
    )
