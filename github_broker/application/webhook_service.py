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
            try:
                self._process_issue_event(payload)
                logger.info(f"Successfully processed webhook payload for action: {payload.get('action', 'N/A')}")
                return payload
            except Exception as e:
                logger.error(f"Error processing webhook payload: {e}", exc_info=True)
                # TODO: エラー処理とリトライ機構（Dead Letter Queueなど）を実装
                return None
        else:
            logger.info("Webhook queue is empty in Redis.")
            return None

    def _process_issue_event(self, payload: dict):
        """
        Issue関連のWebhookイベントを処理し、Redisキャッシュを更新します。
        """
        action = payload.get("action")
        issue = payload.get("issue")

        if not issue:
            logger.warning(f"Issue data not found in payload for action: {action}")
            return

        issue_id = issue.get("id")
        if not issue_id:
            logger.warning(f"Issue ID not found in payload for action: {action}")
            return

        if action in ["opened", "edited", "reopened"]:
            # Issueの作成または更新
            self.redis_client.set_issue(str(issue_id), json.dumps(issue))
            logger.info(f"Issue {issue_id} {action} and cached in Redis.")
        elif action == "closed":
            # Issueの削除
            self.redis_client.delete_issue(str(issue_id))
            logger.info(f"Issue {issue_id} {action} and removed from Redis cache.")
        elif action == "deleted":
            # Issueの削除
            self.redis_client.delete_issue(str(issue_id))
            logger.info(f"Issue {issue_id} {action} and removed from Redis cache.")
        else:
            logger.info(f"Unhandled webhook action: {action}. No cache update performed.")
