import hmac
import hashlib
import os
import logging
import json
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

        sha_name, signature_hash = signature.split('=', 1)
        if sha_name != 'sha256':
            logger.warning(f"Unsupported signature algorithm: {sha_name}")
            return False

        mac = hmac.new(self.webhook_secret.encode('utf-8'), payload_body, hashlib.sha256)
        return hmac.compare_digest(mac.hexdigest(), signature_hash)

    def enqueue_payload(self, payload: dict):
        """
        受信したWebhookペイロードをRedisキューに格納します。
        """
        payload_str = json.dumps(payload)
        self.redis_client.rpush_event(self.webhook_queue_name, payload_str)
        logger.info(f"Webhook payload enqueued to Redis. Queue: {self.webhook_queue_name}")

    def process_next_payload(self) -> dict | None:
        """
        Redisキューから次のペイロードを取り出して処理します。（非同期処理のプレースホルダー）
        """
        payload_str = self.redis_client.lpop_event(self.webhook_queue_name)
        if payload_str:
            payload = json.loads(payload_str)
            logger.info(f"Processing webhook payload: {payload.get('action', 'N/A')}")
            # ここに実際の非同期処理ロジックを実装
            return payload
        else:
            logger.info("Webhook queue is empty in Redis.")
            return None
