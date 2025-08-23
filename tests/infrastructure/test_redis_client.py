import unittest
from unittest.mock import MagicMock

from github_broker.infrastructure.redis_client import RedisClient


class TestRedisClient(unittest.TestCase):
    def setUp(self):
        self.mock_redis_instance = MagicMock()
        self.redis_client = RedisClient(self.mock_redis_instance)

    def test_acquire_lock(self):
        # Arrange
        lock_key = "test_lock"
        value = "locked"
        timeout = 300
        self.mock_redis_instance.set.return_value = True

        # Act
        result = self.redis_client.acquire_lock(lock_key, value, timeout)

        # Assert
        self.mock_redis_instance.set.assert_called_once_with(
            lock_key, value, ex=timeout, nx=True
        )
        self.assertTrue(result)

    def test_release_lock(self):
        # Arrange
        lock_key = "test_lock"
        self.mock_redis_instance.delete.return_value = 1

        # Act
        result = self.redis_client.release_lock(lock_key)

        # Assert
        self.mock_redis_instance.delete.assert_called_once_with(lock_key)
        self.assertTrue(result)

    def test_release_lock_not_found(self):
        # Arrange
        lock_key = "test_lock"
        self.mock_redis_instance.delete.return_value = 0

        # Act
        result = self.redis_client.release_lock(lock_key)

        # Assert
        self.assertFalse(result)

    def test_get_value(self):
        # Arrange
        key = "test_key"
        value = b"test_value"
        self.mock_redis_instance.get.return_value = value

        # Act
        result = self.redis_client.get_value(key)

        # Assert
        self.mock_redis_instance.get.assert_called_once_with(key)
        self.assertEqual(result, value.decode("utf-8"))

    def test_get_value_none(self):
        # Arrange
        key = "test_key"
        self.mock_redis_instance.get.return_value = None

        # Act
        result = self.redis_client.get_value(key)

        # Assert
        self.assertIsNone(result)

    def test_set_value(self):
        # Arrange
        key = "test_key"
        value = "test_value"
        timeout = 300

        # Act
        self.redis_client.set_value(key, value, timeout)

        # Assert
        self.mock_redis_instance.set.assert_called_once_with(key, value, ex=timeout)

    def test_delete_key(self):
        # Arrange
        key = "test_key"

        # Act
        self.redis_client.delete_key(key)

        # Assert
        self.mock_redis_instance.delete.assert_called_once_with(key)


if __name__ == "__main__":
    unittest.main()
