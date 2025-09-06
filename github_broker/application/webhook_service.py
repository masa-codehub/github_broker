import hashlib
import hmac
import json
import logging
import os

from github_broker.infrastructure.redis_client import RedisClient

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self, redis_client: RedisClient):
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        if not self.webhook_secret:
            raise ValueError("GITHUB_WEBHOOK_SECRET環境変数が設定されていません。")
        self.redis_client = redis_client
        self.webhook_queue_name = "webhook_events"

    def verify_signature(self, signature: str, payload_body: bytes) -> bool:
        """
        GitHub Webhookの署名を検証します。
        """
        if not signature:
            return False

        try:
            sha_name, signature_hash = signature.split("=", 1)
        except ValueError:
            logger.warning(f"Malformed signature header: {signature}")
            return False
        if sha_name != "sha256":
            logger.warning(f"Unsupported signature algorithm: {sha_name}")
            return False

        mac = hmac.new(
            self.webhook_secret.encode("utf-8"), payload_body, hashlib.sha256
        )
        return hmac.compare_digest(mac.hexdigest(), signature_hash)

    def enqueue_payload(self, payload: dict):
        """
        受信したWebhookペイロードをRedisキューに格納します。
        """
        payload_str = json.dumps(payload)
        self.redis_client.rpush_event(self.webhook_queue_name, payload_str)
        logger.info(
            f"Webhook payload enqueued to Redis. Queue: {self.webhook_queue_name}"
        )
