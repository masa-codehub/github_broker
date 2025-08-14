import os
import redis

class RedisClient:
    """
    A client to interact with Redis for distributed locking and state management.
    """
    def __init__(self, lock_timeout: int = 30):
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        self._client = redis.Redis(host=host, port=port, db=0, decode_responses=True)
        self.lock_key = "github_broker_lock"
        self.lock_timeout = lock_timeout

    def acquire_lock(self) -> bool:
        """
        Tries to acquire a global lock.
        Returns True if the lock was acquired, False otherwise.
        """
        # SETNX (SET if Not eXists)
        return self._client.set(self.lock_key, "locked", ex=self.lock_timeout, nx=True)

    def release_lock(self) -> bool:
        """
        Releases the global lock.
        """
        self._client.delete(self.lock_key)
        return True

    def set_assignment(self, agent_id: str, issue_id: int):
        """
        Stores the assignment of an issue to an agent.
        """
        key = f"agent_assignment:{agent_id}"
        self._client.set(key, issue_id)

    def get_assignment(self, agent_id: str) -> int | None:
        """
        Retrieves the issue ID assigned to an agent.
        """
        key = f"agent_assignment:{agent_id}"
        issue_id = self._client.get(key)
        return int(issue_id) if issue_id else None
