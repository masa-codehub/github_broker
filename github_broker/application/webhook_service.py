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
            raise ValueError("GITHUB_WEBHOOK_SECRET 環境変数が設定されていません。")
        self.queue = deque()

    def verify_signature(self, signature: str, payload: bytes) -> bool:
        """
        GitHub Webhookの署名を検証します。
        """
        if not signature:
            logger.warning("X-Hub-Signature-256 ヘッダーがありません。")
            return False

        try:
            sha_name, signature_hash = signature.split('=', 1)
            if sha_name != 'sha256':
                logger.warning(f"不明なハッシュタイプ: {sha_name}")
                return False
        except ValueError:
            logger.warning("X-Hub-Signature-256 ヘッダーの形式が不正です。")
            return False

        mac = hmac.new(self.webhook_secret.encode('utf-8'), payload, hashlib.sha256)
        return hmac.compare_digest(mac.hexdigest(), signature_hash)

    def enqueue_payload(self, payload: dict):
        """
        受信したWebhookペイロードをキューに格納します。
        """
        self.queue.append(payload)
        logger.info(f"Webhookペイロードをキューに格納しました。現在のキューサイズ: {len(self.queue)}")

    def process_next_payload(self):
        """
        キューから次のペイロードを取り出して処理します。（現時点ではログ出力のみ）
        """
        if self.queue:
            payload = self.queue.popleft()
            logger.info(f"キューからペイロードを取り出しました: {payload.get('action', 'N/A')}")
            # ここに非同期処理のロジックを追加する
            return payload
        else:
            logger.info("キューは空です。")
            return None