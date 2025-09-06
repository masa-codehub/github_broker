import os
import hmac
import hashlib
from unittest.mock import patch
import pytest
from collections import deque

from github_broker.application.webhook_service import WebhookService

@pytest.fixture
def webhook_service():
    """WebhookServiceのテストインスタンスを提供します。"""
    with patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": "test_secret"}):
        service = WebhookService()
        service.queue = deque() # テスト用にキューを初期化
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

def test_enqueue_payload(webhook_service):
    """ペイロードがキューに正しく追加されることをテストします。"""
    payload = {"action": "opened", "issue": {"number": 1}}
    webhook_service.enqueue_payload(payload)
    assert len(webhook_service.queue) == 1
    assert webhook_service.queue[0] == payload

def test_process_next_payload_with_items(webhook_service):
    """キューにアイテムがある場合に正しく処理されることをテストします。"""
    payload1 = {"action": "opened", "issue": {"number": 1}}
    payload2 = {"action": "closed", "issue": {"number": 2}}
    webhook_service.enqueue_payload(payload1)
    webhook_service.enqueue_payload(payload2)

    processed_payload = webhook_service.process_next_payload()
    assert processed_payload == payload1
    assert len(webhook_service.queue) == 1
    assert webhook_service.queue[0] == payload2

def test_process_next_payload_empty_queue(webhook_service):
    """キューが空の場合にNoneが返されることをテストします。"""
    processed_payload = webhook_service.process_next_payload()
    assert processed_payload is None
    assert len(webhook_service.queue) == 0

def test_webhook_secret_not_set():
    """GITHUB_WEBHOOK_SECRETが設定されていない場合にValueErrorが発生することをテストします。"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="GITHUB_WEBHOOK_SECRET環境変数が設定されていません。"):
            WebhookService()
