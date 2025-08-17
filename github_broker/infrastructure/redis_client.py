import logging

import redis


class RedisClient:
    """
    A client for Redis, used for distributed locking.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        try:
            self.client = redis.Redis(host=host, port=port, db=db)
            self.client.ping()
            logging.info(f"Successfully connected to Redis at {host}:{port}")
        except redis.exceptions.ConnectionError as e:
            logging.error(f"Could not connect to Redis: {e}")
            raise

    def acquire_lock(self, lock_key="github_broker_lock", timeout=30) -> bool:
        """
        Acquires a distributed lock.

        Args:
            lock_key (str): The key to use for the lock.
            timeout (int): The lock's time-to-live in seconds.

        Returns:
            bool: True if the lock was acquired, False otherwise.
        """
        # SETNX sets the key only if it does not already exist.
        # It returns 1 if the lock was acquired, 0 otherwise.
        # `ex=timeout` sets an expiration time on the key.
        return self.client.set(lock_key, "locked", ex=timeout, nx=True)

    def release_lock(self, lock_key="github_broker_lock"):
        """
        Releases the distributed lock.
        """
        self.client.delete(lock_key)
