import os
import hmac
import hashlib
from unittest.mock import patch, MagicMock
import pytest
import json

from github_broker.application.webhook_service import WebhookService
from github_broker.infrastructure.redis_client import RedisClient

@pytest.fixture
def mock_redis_client():
    """RedisClientのモックを提供します。"""
    return MagicMock(spec=RedisClient)

@pytest.fixture
def webhook_service(mock_redis_client):
    """WebhookServiceのテストインスタンスを提供します。"""
    with patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": "test_secret"}):
        service = WebhookService(redis_client=mock_redis_client)
        return service

def generate_signature(secret: str, payload_body: bytes) -> str:
    """テスト用の署名を生成します。"""
    mac = hmac.new(secret.encode('utf-8'), payload_body, hashlib.sha256)
    return f"sha256={mac.hexdigest()}"

def test_verify_signature_valid(webhook_service):
    """有効な署名が正しく検証されることをテストします。"""
    secret = "test_secret"
    payload_body = b'{"test": "payload"}'
    signature = generate_signature(secret, payload_body)
    assert webhook_service.verify_signature(signature, payload_body)

def test_verify_signature_invalid(webhook_service):
    """無効な署名が正しく検証されないことをテストします。"""
    secret = "test_secret"
    payload_body = b'{"test": "payload"}'
    invalid_payload_body = b'{"test": "invalid"}'
    signature = generate_signature(secret, payload_body)
    assert not webhook_service.verify_signature(signature, invalid_payload_body)

def test_verify_signature_wrong_secret(webhook_service):
    """異なるシークレットで生成された署名が検証されないことをテストします。"""
    wrong_secret = "wrong_secret"
    payload_body = b'{"test": "payload"}'
    signature = generate_signature(wrong_secret, payload_body)
    assert not webhook_service.verify_signature(signature, payload_body)

def test_verify_signature_no_signature(webhook_service):
    """署名がない場合に検証が失敗することをテストします。"""
    payload_body = b'{"test": "payload"}'
    assert not webhook_service.verify_signature(None, payload_body)

def test_verify_signature_unsupported_algorithm(webhook_service):
    """サポートされていないアルゴリズムの署名が検証されないことをテストします。"""
    payload_body = b'{"test": "payload"}'
    signature = "sha1=invalid_hash" # サポートされていないアルゴリズム
    assert not webhook_service.verify_signature(signature, payload_body)

def test_enqueue_payload(webhook_service, mock_redis_client):
    """ペイロードがRedisキューに正しく追加されることをテストします。"""
    payload = {"action": "opened", "issue": {"number": 1}}
    webhook_service.enqueue_payload(payload)
    mock_redis_client.rpush_event.assert_called_once_with(webhook_service.webhook_queue_name, json.dumps(payload))

def test_process_next_payload_with_items(webhook_service, mock_redis_client):
    """キューにアイテムがある場合に正しく処理されることをテストします。"""
    payload1 = {"action": "opened", "issue": {"number": 1}}
    payload2 = {"action": "closed", "issue": {"number": 2}}
    mock_redis_client.lpop_event.side_effect = [json.dumps(payload1), json.dumps(payload2), None]

    processed_payload = webhook_service.process_next_payload()
    assert processed_payload == payload1
    mock_redis_client.lpop_event.assert_called_once_with(webhook_service.webhook_queue_name)

def test_process_next_payload_empty_queue(webhook_service, mock_redis_client):
    """キューが空の場合にNoneが返されることをテストします。"""
    mock_redis_client.lpop_event.return_value = None
    processed_payload = webhook_service.process_next_payload()
    assert processed_payload is None
    mock_redis_client.lpop_event.assert_called_once_with(webhook_service.webhook_queue_name)

def test_process_next_payload_handles_issue_opened(webhook_service, mock_redis_client):
    """
    process_next_payloadがopenedアクションのIssueを正しく処理することをテストします。
    """
    issue_payload = {
        "action": "opened",
        "issue": {"id": 123, "title": "Test Issue", "state": "open"}
    }
    mock_redis_client.lpop_event.return_value = json.dumps(issue_payload)

    processed_payload = webhook_service.process_next_payload()

    assert processed_payload == issue_payload
    mock_redis_client.set_issue.assert_called_once_with("123", json.dumps(issue_payload["issue"]))
    mock_redis_client.delete_issue.assert_not_called()

def test_process_next_payload_handles_issue_edited(webhook_service, mock_redis_client):
    """
    process_next_payloadがeditedアクションのIssueを正しく処理することをテストします。
    """
    issue_payload = {
        "action": "edited",
        "issue": {"id": 123, "title": "Edited Test Issue", "state": "open"}
    }
    mock_redis_client.lpop_event.return_value = json.dumps(issue_payload)

    processed_payload = webhook_service.process_next_payload()

    assert processed_payload == issue_payload
    mock_redis_client.set_issue.assert_called_once_with("123", json.dumps(issue_payload["issue"]))
    mock_redis_client.delete_issue.assert_not_called()

def test_process_next_payload_handles_issue_reopened(webhook_service, mock_redis_client):
    """
    process_next_payloadがreopenedアクションのIssueを正しく処理することをテストします。
    """
    issue_payload = {
        "action": "reopened",
        "issue": {"id": 123, "title": "Reopened Test Issue", "state": "open"}
    }
    mock_redis_client.lpop_event.return_value = json.dumps(issue_payload)

    processed_payload = webhook_service.process_next_payload()

    assert processed_payload == issue_payload
    mock_redis_client.set_issue.assert_called_once_with("123", json.dumps(issue_payload["issue"]))
    mock_redis_client.delete_issue.assert_not_called()

def test_process_next_payload_handles_issue_closed(webhook_service, mock_redis_client):
    """
    process_next_payloadがclosedアクションのIssueを正しく処理することをテストします。
    """
    issue_payload = {
        "action": "closed",
        "issue": {"id": 123, "title": "Closed Test Issue", "state": "closed"}
    }
    mock_redis_client.lpop_event.return_value = json.dumps(issue_payload)

    processed_payload = webhook_service.process_next_payload()

    assert processed_payload == issue_payload
    mock_redis_client.delete_issue.assert_called_once_with("123")
    mock_redis_client.set_issue.assert_not_called()

def test_process_next_payload_handles_issue_deleted(webhook_service, mock_redis_client):
    """
    process_next_payloadがdeletedアクションのIssueを正しく処理することをテストします。
    """
    issue_payload = {
        "action": "deleted",
        "issue": {"id": 123, "title": "Deleted Test Issue", "state": "deleted"}
    }
    mock_redis_client.lpop_event.return_value = json.dumps(issue_payload)

    processed_payload = webhook_service.process_next_payload()

    assert processed_payload == issue_payload
    mock_redis_client.delete_issue.assert_called_once_with("123")
    mock_redis_client.set_issue.assert_not_called()

def test_process_next_payload_handles_unhandled_action(webhook_service, mock_redis_client):
    """
    process_next_payloadが未処理のアクションをスキップすることをテストします。
    """
    issue_payload = {
        "action": "assigned", # 未処理のアクション
        "issue": {"id": 123, "title": "Assigned Test Issue", "state": "open"}
    }
    mock_redis_client.lpop_event.return_value = json.dumps(issue_payload)

    processed_payload = webhook_service.process_next_payload()

    assert processed_payload == issue_payload
    mock_redis_client.set_issue.assert_not_called()
    mock_redis_client.delete_issue.assert_not_called()

def test_process_next_payload_handles_missing_issue_data(webhook_service, mock_redis_client):
    """
    process_next_payloadがissueデータがないペイロードを処理することをテストします。
    """
    issue_payload = {
        "action": "opened",
        "repository": {"id": 456} # issueデータがない
    }
    mock_redis_client.lpop_event.return_value = json.dumps(issue_payload)

    processed_payload = webhook_service.process_next_payload()

    assert processed_payload == issue_payload
    mock_redis_client.set_issue.assert_not_called()
    mock_redis_client.delete_issue.assert_not_called()

def test_process_next_payload_handles_missing_issue_id(webhook_service, mock_redis_client):
    """
    process_next_payloadがissue_idがないペイロードを処理することをテストします。
    """
    issue_payload = {
        "action": "opened",
        "issue": {"title": "Test Issue without ID"} # idがない
    }
    mock_redis_client.lpop_event.return_value = json.dumps(issue_payload)

    processed_payload = webhook_service.process_next_payload()

    assert processed_payload == issue_payload
    mock_redis_client.set_issue.assert_not_called()
    mock_redis_client.delete_issue.assert_not_called()

def test_process_next_payload_error_handling(webhook_service, mock_redis_client):
    """
    process_next_payloadが処理中のエラーを適切にハンドリングすることをテストします。
    """
    issue_payload = {
        "action": "opened",
        "issue": {"id": 123, "title": "Test Issue", "state": "open"}
    }
    mock_redis_client.lpop_event.return_value = json.dumps(issue_payload)
    # set_issueが例外を発生させるように設定
    mock_redis_client.set_issue.side_effect = Exception("Redis error")

    processed_payload = webhook_service.process_next_payload()

    assert processed_payload is None # エラーが発生したためNoneが返される
    mock_redis_client.set_issue.assert_called_once_with("123", json.dumps(issue_payload["issue"]))
    mock_redis_client.delete_issue.assert_not_called()
