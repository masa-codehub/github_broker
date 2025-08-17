"""
Task Service to handle business logic related to tasks.
"""

import logging
from uuid import uuid4

from github_broker.application.exceptions import LockAcquisitionError
from github_broker.infrastructure.github_client import GitHubAppClient
from github_broker.infrastructure.redis_client import RedisClient

logger = logging.getLogger(__name__)


class TaskService:
    """
    A service class for handling business logic related to tasks.
    """

    def __init__(self, redis_client: RedisClient, github_client: GitHubAppClient):
        self.redis_client = redis_client
        self.github_client = github_client
        self.lock_key = "task_lock"
        self.task_id_key = "task_id"

    def request_task(self) -> str:
        """
        Requests a task. If a task is already running, raises an exception.
        Otherwise, it acquires a lock and returns a new task ID.
        """
        logger.info("Attempting to acquire lock for a new task.")
        if not self.redis_client.acquire_lock(self.lock_key, str(uuid4())):
            logger.warning("Failed to acquire lock. A task may already be in progress.")
            raise LockAcquisitionError(
                "Failed to acquire lock. Another task is likely running."
            )

        task_id = str(uuid4())
        self.redis_client.set_value(self.task_id_key, task_id)
        logger.info(f"Lock acquired. New task created with ID: {task_id}")
        return task_id

    def get_running_task(self) -> str | None:
        """
        Retrieves the ID of the currently running task.
        """
        task_id = self.redis_client.get_value(self.task_id_key)
        logger.info(f"Retrieved running task ID: {task_id}")
        return task_id

    def release_task(self):
        """
        Releases the lock for the current task.
        """
        logger.info("Releasing task lock.")
        if not self.redis_client.release_lock(self.lock_key):
            logger.error(
                "Failed to release lock. It may have expired or been released by another process."
            )
            # Depending on requirements, we might want to raise an exception here.
            # For now, we just log the error.
        else:
            logger.info("Lock released successfully.")
        self.redis_client.delete_key(self.task_id_key)
