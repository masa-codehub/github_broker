import hmac
import hashlib
import os
import logging
from collections import deque

logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self):
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        if not self.webhook_secret:
            raise ValueError("GITHUB_WEBHOOK_SECRET環境変数が設定されていません。")
        self.queue = deque() # シンプルなインメモリキュー

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
        受信したWebhookペイロードをキューに格納します。
        """
        self.queue.append(payload)
        logger.info(f"Webhook payload enqueued. Current queue size: {len(self.queue)}")

    def process_next_payload(self):
        """
        キューから次のペイロードを取り出して処理します。（非同期処理のプレースホルダー）
        """
        if self.queue:
            payload = self.queue.popleft()
            logger.info(f"Processing webhook payload: {payload.get('action', 'N/A')}")
            # ここに実際の非同期処理ロジックを実装
            return payload
        else:
            logger.info("Webhook queue is empty.")
            return None
