import hmac
import hashlib
import os
import queue

class WebhookService:
    def __init__(self):
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        if not self.webhook_secret:
            raise ValueError("GITHUB_WEBHOOK_SECRET environment variable not set.")
        self.payload_queue = queue.Queue()

    def verify_signature(self, signature: str, payload: bytes) -> bool:
        if not signature:
            return False

        sha_name, signature = signature.split('=', 1)
        if sha_name != 'sha256':
            return False

        mac = hmac.new(self.webhook_secret.encode('utf-8'), payload, hashlib.sha256)
        return hmac.compare_digest(mac.hexdigest(), signature)

    def enqueue_payload(self, payload: dict):
        self.payload_queue.put(payload)

    def get_queued_payload(self):
        if not self.payload_queue.empty():
            return self.payload_queue.get()
        return None