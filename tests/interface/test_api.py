import hashlib
import hmac
import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

# DIコンテナをテストモードで読み込むために、最初に環境変数を設定
os.environ["TESTING"] = "true"

from github_broker.application.exceptions import LockAcquisitionError
from github_broker.application.task_service import TaskService
from github_broker.application.webhook_service import WebhookService
from github_broker.infrastructure.di_container import (
    container,  # DIコンテナをインポート
)
from github_broker.interface.api import app, get_task_service
from github_broker.interface.models import TaskResponse

# WebhookServiceのモックをDIコンテナに登録
# このモックはファイルスコープで、すべてのテストで使用される
mock_webhook_service_instance = MagicMock(spec=WebhookService)
container.register(WebhookService, instance=mock_webhook_service_instance)


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_webhook_mock():
    """
    各テストの実行前に、ファイルスコープのWebhookServiceモックの状態をリセットする。
    これにより、テスト間の呼び出し履歴の干渉を防ぐ。
    """
    mock_webhook_service_instance.reset_mock()


@pytest.fixture
def mock_task_service():
    """TaskServiceの依存関係をモックするためのフィクスチャ。"""
    mock_service = MagicMock(spec=TaskService)
    app.dependency_overrides[get_task_service] = lambda: mock_service
    yield mock_service
    # ティアダウン：オーバーライドをクリーンアップ
    del app.dependency_overrides[get_task_service]


def generate_signature(secret: str, payload_body: bytes) -> str:
    """テスト用の署名を生成します。"""
    mac = hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


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


def test_github_webhook_endpoint_success():
    """/api/v1/webhook/githubエンドポイントへの成功したWebhookリクエストをテストします。"""
    # Arrange
    payload = {"action": "opened", "issue": {"number": 1}}
    payload_bytes = b'{"action": "opened", "issue": {"number": 1}}'
    signature = generate_signature("test_secret", payload_bytes)

    mock_webhook_service_instance.verify_signature.return_value = True

    # Act
    response = client.post(
        "/api/v1/webhook/github",
        headers={"X-Hub-Signature-256": signature},
        content=payload_bytes,
    )

    # Assert
    assert response.status_code == 202
    assert response.json() == {"message": "Webhook received and enqueued."}
    mock_webhook_service_instance.verify_signature.assert_called_once_with(
        signature, payload_bytes
    )
    mock_webhook_service_instance.enqueue_payload.assert_called_once_with(payload)


def test_github_webhook_endpoint_no_signature():
    """X-Hub-Signature-256ヘッダーがない場合のWebhookリクエストをテストします。"""
    # Arrange
    payload_bytes = b'{"action": "opened", "issue": {"number": 1}}'

    # Act
    response = client.post(
        "/api/v1/webhook/github",
        content=payload_bytes,
    )

    # Assert
    assert response.status_code == 401
    assert response.json() == {"detail": "X-Hub-Signature-256 header missing"}
    mock_webhook_service_instance.verify_signature.assert_not_called()
    mock_webhook_service_instance.enqueue_payload.assert_not_called()


def test_github_webhook_endpoint_invalid_signature():
    """署名検証が失敗した場合のWebhookリクエストをテストします。"""
    # Arrange
    payload_bytes = b'{"action": "opened", "issue": {"number": 1}}'
    signature = "sha256=invalid_signature"

    mock_webhook_service_instance.verify_signature.return_value = False

    # Act
    response = client.post(
        "/api/v1/webhook/github",
        headers={"X-Hub-Signature-256": signature},
        content=payload_bytes,
    )

    # Assert
    assert response.status_code == 401
    assert response.json() == {"detail": "Webhook signature verification failed"}
    mock_webhook_service_instance.verify_signature.assert_called_once_with(
        signature, payload_bytes
    )
    mock_webhook_service_instance.enqueue_payload.assert_not_called()


def test_github_webhook_endpoint_invalid_json():
    """無効なJSONペイロードのWebhookリクエストをテストします。"""
    # Arrange
    payload_bytes = b"invalid json"
    signature = generate_signature("test_secret", payload_bytes)

    mock_webhook_service_instance.verify_signature.return_value = True

    # Act
    response = client.post(
        "/api/v1/webhook/github",
        headers={"X-Hub-Signature-256": signature},
        content=payload_bytes,
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid JSON payload"}
    mock_webhook_service_instance.verify_signature.assert_called_once_with(
        signature, payload_bytes
    )
    mock_webhook_service_instance.enqueue_payload.assert_not_called()
