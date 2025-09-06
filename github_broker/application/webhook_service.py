import logging
import os
import hmac
import hashlib
from queue import Queue

logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self):
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        if not self.webhook_secret:
            raise ValueError("GITHUB_WEBHOOK_SECRET 環境変数が設定されていません。")
        self.webhook_queue = Queue() # シンプルなインメモリキュー

    def verify_signature(self, signature: str, payload_body: bytes) -> bool:
        """
        GitHub Webhookの署名を検証します。
        """
        if not signature:
            logger.warning("X-Hub-Signature-256 ヘッダーがありません。")
            return False

        sha_name, signature = signature.split('=', 1)
        if sha_name != 'sha256':
            logger.warning(f"不明なハッシュタイプ: {sha_name}")
            return False

        mac = hmac.new(self.webhook_secret.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
        return hmac.compare_digest(mac.hexdigest(), signature)

    def enqueue_webhook_payload(self, payload: dict):
        """
        受信したWebhookペイロードをキューに格納します。
        """
        logger.info("Webhookペイロードをキューに格納します。")
        self.webhook_queue.put(payload)
        logger.info(f"現在のキューサイズ: {self.webhook_queue.qsize()}")

    def process_next_webhook(self):
        """
        キューから次のWebhookペイロードを取り出して処理します。（仮実装）
        """
        if not self.webhook_queue.empty():
            payload = self.webhook_queue.get()
            logger.info(f"キューからペイロードを取り出しました: {payload.get('action')}")
            # ここに実際のWebhook処理ロジックを追加
            return payload
        return None