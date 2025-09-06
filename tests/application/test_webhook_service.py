import os
import hmac
import hashlib
from unittest.mock import patch, MagicMock

import pytest

from github_broker.application.webhook_service import WebhookService

@pytest.fixture
def webhook_service():
    """WebhookServiceのテストインスタンスを提供します。"""
    # 環境変数 GITHUB_WEBHOOK_SECRET を設定
    with patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": "test_secret"}):
        return WebhookService()

def generate_signature(secret: str, payload_body: bytes) -> str:
    """テスト用の署名を生成します。"""
    mac = hmac.new(secret.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    return f"sha256={mac.hexdigest()}"

def test_verify_signature_valid(webhook_service):
    """有効な署名が正しく検証されることをテストします。"""
    secret = webhook_service.webhook_secret # 修正
    payload_body = b'{"test": "payload"}'
    signature = generate_signature(secret, payload_body)

    assert webhook_service.verify_signature(signature, payload_body) is True

def test_verify_signature_invalid_secret(webhook_service):
    """不正なシークレットによる署名が検証に失敗することをテストします。"""
    payload_body = b'{"test": "payload"}'
    # 異なるシークレットで署名を生成
    signature = generate_signature("wrong_secret", payload_body)

    assert webhook_service.verify_signature(signature, payload_body) is False

def test_verify_signature_invalid_payload(webhook_service):
    """ペイロードが改ざんされた署名が検証に失敗することをテストします。"""
    secret = webhook_service.webhook_secret # 修正
    payload_body = b'{"test": "payload"}'
    signature = generate_signature(secret, payload_body)
    
    # ペイロードを改ざん
    modified_payload_body = b'{"test": "modified_payload"}'

    assert webhook_service.verify_signature(signature, modified_payload_body) is False

def test_verify_signature_missing_header(webhook_service):
    """X-Hub-Signature-256 ヘッダーがない場合に検証に失敗することをテストします。"""
    payload_body = b'{"test": "payload"}'
    assert webhook_service.verify_signature(None, payload_body) is False

def test_verify_signature_unsupported_hash_type(webhook_service):
    """サポートされていないハッシュタイプの場合に検証に失敗することをテストします。"""
    payload_body = b'{"test": "payload"}'
    signature = "sha1=some_hash" # sha1 はサポートされていない
    assert webhook_service.verify_signature(signature, payload_body) is False

def test_enqueue_webhook_payload(webhook_service):
    """Webhookペイロードがキューに正しく格納されることをテストします。"""
    payload = {"action": "opened", "issue": {"number": 1}}
    webhook_service.enqueue_webhook_payload(payload)

    assert not webhook_service.webhook_queue.empty()
    assert webhook_service.webhook_queue.qsize() == 1
    assert webhook_service.webhook_queue.get() == payload

def test_process_next_webhook_with_payload(webhook_service):
    """キューにペイロードがある場合に正しく処理されることをテストします。"""
    payload = {"action": "closed", "issue": {"number": 2}}
    webhook_service.enqueue_webhook_payload(payload)

    processed_payload = webhook_service.process_next_webhook()
    assert processed_payload == payload
    assert webhook_service.webhook_queue.empty()

def test_process_next_webhook_empty_queue(webhook_service):
    """キューが空の場合にNoneが返されることをテストします。"""
    processed_payload = webhook_service.process_next_webhook()
    assert processed_payload is None