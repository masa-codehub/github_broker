import os
import hmac
import hashlib
import json
from queue import Queue

class WebhookService:
    def __init__(self):
        self.secret = os.environ.get("GITHUB_WEBHOOK_SECRET")
        if not self.secret:
            raise ValueError("GITHUB_WEBHOOK_SECRET environment variable not set.")
        self.queue = Queue()

    def verify_signature(self, signature: str, payload: bytes) -> bool:
        if not signature:
            return False

        # Extract the algorithm and hash from the signature
        try:
            algorithm, hash_value = signature.split("=", 1)
        except ValueError:
            return False

        if algorithm != "sha256":
            return False

        # Calculate the expected signature
        hmac_obj = hmac.new(self.secret.encode('utf-8'), payload, hashlib.sha256)
        expected_signature = hmac_obj.hexdigest()

        # Compare the calculated signature with the provided signature
        return hmac.compare_digest(expected_signature, hash_value)

    def process_webhook(self, signature: str, payload: bytes):
        if not self.verify_signature(signature, payload):
            raise ValueError("Invalid signature")

        try:
            payload_dict = json.loads(payload)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON payload")

        self.queue.put(payload_dict)
