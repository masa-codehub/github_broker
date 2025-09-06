import hmac
import hashlib
import os
from collections import deque
from typing import Dict, Any

class WebhookService:
    def __init__(self):
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        if not self.webhook_secret:
            raise ValueError("GITHUB_WEBHOOK_SECRET environment variable not set.")
        self.queue = deque() # Simple in-memory queue

    def verify_signature(self, signature: str, payload: bytes) -> bool:
        """
        Verifies the GitHub webhook signature.
        """
        if not signature:
            return False

        sha_name, signature_hash = signature.split('=', 1)
        if sha_name != 'sha256':
            return False

        mac = hmac.new(self.webhook_secret.encode('utf-8'), payload, hashlib.sha256)
        return hmac.compare_digest(mac.hexdigest(), signature_hash)

    def enqueue_webhook_payload(self, payload: Dict[str, Any]):
        """
        Enqueues the parsed webhook payload for asynchronous processing.
        """
        self.queue.append(payload)
        print(f"Webhook payload enqueued. Current queue size: {len(self.queue)}")

    def process_next_payload(self) -> Dict[str, Any] | None:
        """
        Retrieves and removes the next payload from the queue.
        (For demonstration/testing purposes, actual processing would be async)
        """
        if self.queue:
            return self.queue.popleft()
        return None
