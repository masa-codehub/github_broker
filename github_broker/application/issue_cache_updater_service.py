import json
import logging
import threading
import time

from github_broker.infrastructure.redis_client import RedisClient

logger = logging.getLogger(__name__)


class IssueCacheUpdaterService:
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        self.webhook_queue_name = "webhook_events"
        self._running = threading.Event()
        self._thread = None

    def start(self):
        if self.is_running():
            logger.warning("Service is already running.")
            return
        logger.info("IssueCacheUpdaterService starting.")
        self._running.set()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("IssueCacheUpdaterService started.")

    def stop(self):
        if not self.is_running():
            logger.warning("Service is not running.")
            return
        logger.info("IssueCacheUpdaterService stopping.")
        self._running.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join()
        logger.info("IssueCacheUpdaterService stopped.")

    def is_running(self) -> bool:
        return self._running.is_set()

    def _run_loop(self):
        while self.is_running():
            try:
                payload_str = self.redis_client.blpop_event(
                    self.webhook_queue_name, timeout=1
                )
                if payload_str:
                    self._process_payload(payload_str)
            except Exception as e:
                logger.error(
                    f"An unexpected error occurred in the run loop: {e}", exc_info=True
                )
                time.sleep(1)

    def _process_payload(self, payload_str: str):
        try:
            payload = json.loads(payload_str)
            self._process_webhook_payload(payload)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON payload: {e} - Payload: {payload_str}")
        except Exception as e:
            logger.error(f"Error processing webhook payload: {e}", exc_info=True)
            dlq_name = f"{self.webhook_queue_name}_dlq"
            try:
                self.redis_client.rpush_event(dlq_name, payload_str)
                logger.warning(f"Webhook payload moved to DLQ: {dlq_name}")
            except Exception as dlq_e:
                logger.error(
                    f"Failed to move payload to DLQ '{dlq_name}': {dlq_e}",
                    exc_info=True,
                )

    def _process_webhook_payload(self, payload: dict):
        action = payload.get("action")
        issue = payload.get("issue")

        if not issue or not action:
            logger.warning(
                f"Invalid webhook payload: missing issue or action. Payload: {payload}"
            )
            return

        issue_id = issue.get("id")
        if not issue_id:
            logger.warning(
                f"Invalid webhook payload: missing issue id. Payload: {payload}"
            )
            return
        issue_id = str(issue_id)
        issue_data = json.dumps(issue)

        if action in ["opened", "edited", "reopened"]:
            self.redis_client.set_issue(issue_id, issue_data)
            logger.info(f"Issue {issue_id} ({action}) cached/updated.")
        elif action in ["closed", "deleted"]:
            self.redis_client.delete_issue(issue_id)
            logger.info(f"Issue {issue_id} ({action}) deleted from cache.")
        else:
            logger.info(f"Unhandled webhook action: {action} for issue {issue_id}")
