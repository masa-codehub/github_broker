import hashlib
import hmac
import json
import os
from unittest.mock import MagicMock, patch

import pytest

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
    mac = hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256)
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
    signature = "sha1=invalid_hash"  # サポートされていないアルゴリズム
    assert not webhook_service.verify_signature(signature, payload_body)


def test_enqueue_payload(webhook_service, mock_redis_client):
    """ペイロードがRedisキューに正しく追加されることをテストします。"""
    payload = {"action": "opened", "issue": {"number": 1}}
    webhook_service.enqueue_payload(payload)
    mock_redis_client.rpush_event.assert_called_once_with(
        webhook_service.webhook_queue_name, json.dumps(payload)
    )
