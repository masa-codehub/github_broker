import pytest
import os
from github_broker.application.webhook_service import WebhookService

# Mock environment variable for testing
@pytest.fixture(autouse=True)
def set_env():
    os.environ["GITHUB_WEBHOOK_SECRET"] = "test_secret"
    yield
    del os.environ["GITHUB_WEBHOOK_SECRET"]

def generate_signature(secret: str, payload: bytes) -> str:
    import hmac
    import hashlib
    return "sha256=" + hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()

def test_webhook_service_initialization():
    service = WebhookService()
    assert service.secret == "test_secret"
    assert service.queue.empty()

def test_verify_signature_valid():
    service = WebhookService()
    payload = b'{"test": "payload"}'
    signature = generate_signature("test_secret", payload)
    assert service.verify_signature(signature, payload)

def test_verify_signature_invalid_secret():
    service = WebhookService()
    payload = b'{"test": "payload"}'
    signature = generate_signature("wrong_secret", payload)
    assert not service.verify_signature(signature, payload)

def test_verify_signature_invalid_payload():
    service = WebhookService()
    payload = b'{"test": "payload"}'
    wrong_payload = b'{"test": "wrong"}'
    signature = generate_signature("test_secret", wrong_payload)
    assert not service.verify_signature(signature, payload)

def test_verify_signature_no_signature():
    service = WebhookService()
    payload = b'{"test": "payload"}'
    assert not service.verify_signature("", payload)

def test_process_webhook_success():
    service = WebhookService()
    payload_dict = {"action": "opened", "issue": {"number": 1}}
    payload_bytes = b'{"action": "opened", "issue": {"number": 1}}'
    signature = generate_signature("test_secret", payload_bytes)
    
    service.process_webhook(signature, payload_bytes)
    assert service.queue.qsize() == 1
    assert service.queue.get() == payload_dict

def test_process_webhook_invalid_signature_raises_error():
    service = WebhookService()
    payload_bytes = b'{"action": "opened", "issue": {"number": 1}}'
    signature = generate_signature("wrong_secret", payload_bytes)
    
    with pytest.raises(ValueError, match="Invalid signature"):
        service.process_webhook(signature, payload_bytes)
    assert service.queue.empty()

def test_process_webhook_invalid_json_raises_error():
    service = WebhookService()
    payload_bytes = b'invalid json'
    signature = generate_signature("test_secret", payload_bytes)

    with pytest.raises(ValueError, match="Invalid JSON payload"):
        service.process_webhook(signature, payload_bytes)
    assert service.queue.empty()
