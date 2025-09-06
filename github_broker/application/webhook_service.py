import hmac
import hashlib
import os
import json
from queue import Queue

class WebhookService:
    def __init__(self):
        self.secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        if not self.secret:
            raise ValueError("GITHUB_WEBHOOK_SECRET environment variable not set.")
        self.queue = Queue()

    def verify_signature(self, signature: str, payload_bytes: bytes) -> bool:
        """
        Verifies the GitHub webhook signature.
        """
        if not signature:
            return False

        # GitHub sends 'sha256=' prefix
        expected_signature = "sha256=" + hmac.new(
            self.secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)

    def process_webhook(self, signature: str, payload_bytes: bytes):
        """
        Verifies the webhook and queues it for asynchronous processing.
        """
        if not self.verify_signature(signature, payload_bytes):
            raise ValueError("Invalid signature")
        
        try:
            # Parse the payload inside the service
            payload_json = json.loads(payload_bytes.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON payload: {e}")

        # For now, just put the payload into an in-memory queue
        self.queue.put(payload_json)
        print(f"Webhook payload queued. Queue size: {self.queue.qsize()}")
