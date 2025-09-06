import json
import logging
import time
from github_broker.infrastructure.redis_client import RedisClient

logger = logging.getLogger(__name__)

class IssueCacheUpdaterService:
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        self.webhook_queue_name = "webhook_events"
        self.running = False

    def start(self):
        logger.info("IssueCacheUpdaterService started.")
        self.running = True
        while self.running:
            payload_str = self.redis_client.lpop_event(self.webhook_queue_name)
            if payload_str:
                try:
                    payload = json.loads(payload_str)
                    self._process_webhook_payload(payload)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON payload: {e} - Payload: {payload_str}")
                except Exception as e:
                    logger.error(f"Error processing webhook payload: {e} - Payload: {payload_str}")
                    # リトライ機構の考慮: 現時点ではエラーをログに記録し、次のイベントに進む
                    # より堅牢な実装では、Dead Letter Queueへの移動やリトライ回数の管理が必要
            else:
                time.sleep(1) # キューが空の場合は1秒待機

    def stop(self):
        logger.info("IssueCacheUpdaterService stopping.")
        self.running = False

    def _process_webhook_payload(self, payload: dict):
        action = payload.get("action")
        issue = payload.get("issue")

        if not issue or not action:
            logger.warning(f"Invalid webhook payload: missing issue or action. Payload: {payload}")
            return

        issue_id = str(issue.get("id"))
        issue_data = json.dumps(issue)

        if action == "opened" or action == "edited":
            self.redis_client.set_issue(issue_id, issue_data)
            logger.info(f"Issue {issue_id} ({action}) cached/updated.")
        elif action == "closed":
            self.redis_client.delete_issue(issue_id)
            logger.info(f"Issue {issue_id} ({action}) deleted from cache.")
        else:
            logger.info(f"Unhandled webhook action: {action} for issue {issue_id}")
