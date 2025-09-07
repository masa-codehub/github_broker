import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# DIコンテナをテストモードで読み込むために、最初に環境変数を設定
os.environ["TESTING"] = "true"

from github_broker.application.exceptions import LockAcquisitionError
from github_broker.application.task_service import TaskService
from github_broker.interface.api import app, get_task_service
from github_broker.interface.models import TaskResponse

client = TestClient(app)


@pytest.fixture
def mock_task_service():
    """TaskServiceの依存関係をモックするためのフィクスチャ。"""
    mock_service = MagicMock(spec=TaskService)
    app.dependency_overrides[get_task_service] = lambda: mock_service
    yield mock_service
    # ティアダウン：オーバーライドをクリーンアップ
    del app.dependency_overrides[get_task_service]


@pytest.mark.unit
def test_request_task_success(mock_task_service):
    """/request-taskエンドポイントへの成功したタスクリクエストをテストします。"""
    # Arrange
    expected_task = TaskResponse(
        issue_id=123,
        issue_url="http://example.com/issue/123",
        title="テストIssue",
        body="これはテストIssueです。",
        labels=["bug"],
        branch_name="feature/issue-123-test",
    )
    mock_task_service.request_task.return_value = expected_task
    request_body = {
        "agent_id": "test-agent",
        "agent_role": "BACKENDCODER",
        "timeout": 120,
    }

    # Act
    response = client.post("/request-task", json=request_body)

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_task.model_dump(mode="json")
    mock_task_service.request_task.assert_called_once_with(
        agent_id=request_body["agent_id"],
        agent_role=request_body["agent_role"],
        timeout=request_body["timeout"],
    )


@pytest.mark.unit
def test_request_task_no_task_available(mock_task_service):
    """利用可能なタスクがない場合（204 No Content）の/request-taskエンドポイントをテストします。"""
    # Arrange
    mock_task_service.request_task.return_value = None
    request_body = {
        "agent_id": "test-agent",
        "agent_role": "BACKENDCODER",
        "timeout": 120,
    }

    # Act
    response = client.post("/request-task", json=request_body)

    # Assert
    assert response.status_code == 204
    mock_task_service.request_task.assert_called_once_with(
        agent_id=request_body["agent_id"],
        agent_role=request_body["agent_role"],
        timeout=request_body["timeout"],
    )


@pytest.mark.unit
def test_request_task_lock_error(mock_task_service):
    """LockAcquisitionErrorが発生した場合の/request-taskエンドポイントをテストします。"""
    # Arrange
    error_message = "サーバーがビジー状態です。後でもう一度お試しください。"
    mock_task_service.request_task.side_effect = LockAcquisitionError(error_message)
    request_body = {
        "agent_id": "test-agent",
        "agent_role": "BACKENDCODER",
        "timeout": 120,
    }

    # Act
    response = client.post("/request-task", json=request_body)

    # Assert
    assert response.status_code == 503
    assert response.json() == {"message": error_message}
    mock_task_service.request_task.assert_called_once_with(
        agent_id=request_body["agent_id"],
        agent_role=request_body["agent_role"],
        timeout=request_body["timeout"],
    )


@pytest.mark.unit
def test_get_task_service_resolves_instance():
    """get_task_serviceがDIコンテナからTaskServiceのインスタンスを解決できることをテストします。"""
    # Arrange
    # DIコンテナがテスト環境用に設定されていることを確認
    with patch.dict(
        os.environ, {"GITHUB_REPOSITORY": "test/repo", "GITHUB_TOKEN": "fake-token"}
    ):
        # Act
        service = get_task_service()

        # Assert
        assert isinstance(service, TaskService)
