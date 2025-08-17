"""
Unit tests for the TaskService.
"""
import unittest
from unittest.mock import MagicMock

import pytest

from github_broker.application.exceptions import LockAcquisitionError
from github_broker.application.task_service import TaskService

class TestTaskService(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment before each test.
        """
        self.mock_redis_client = MagicMock()
        self.mock_github_client = MagicMock()
        self.task_service = TaskService(
            redis_client=self.mock_redis_client,
            github_client=self.mock_github_client
        )

    def test_request_task_successfully(self):
        """
        Test that a task is requested successfully when the lock is acquired.
        """
        self.mock_redis_client.acquire_lock.return_value = True
        
        task_id = self.task_service.request_task()
        
        self.assertIsNotNone(task_id)
        self.mock_redis_client.acquire_lock.assert_called_once()
        self.mock_redis_client.set_value.assert_called_once()

    def test_request_task_lock_acquisition_fails(self):
        """
        Test that LockAcquisitionError is raised when the lock cannot be acquired.
        """
        self.mock_redis_client.acquire_lock.return_value = False
        
        with pytest.raises(LockAcquisitionError, match="Failed to acquire lock. Another task is likely running."):
            self.task_service.request_task()
        
        self.mock_redis_client.acquire_lock.assert_called_once()
        self.mock_redis_client.set_value.assert_not_called()

    def test_get_running_task(self):
        """
        Test that the running task ID is retrieved correctly.
        """
        expected_task_id = "some-task-id"
        self.mock_redis_client.get_value.return_value = expected_task_id
        
        task_id = self.task_service.get_running_task()
        
        self.assertEqual(task_id, expected_task_id)
        self.mock_redis_client.get_value.assert_called_once_with("task_id")

    def test_release_task_successfully(self):
        """
        Test that the task lock is released successfully.
        """
        self.mock_redis_client.release_lock.return_value = True
        
        self.task_service.release_task()
        
        self.mock_redis_client.release_lock.assert_called_once()
        self.mock_redis_client.delete_key.assert_called_once_with("task_id")

    def test_release_task_fails(self):
        """
        Test that the task lock fails to be released but does not raise an exception.
        """
        self.mock_redis_client.release_lock.return_value = False
        
        self.task_service.release_task()
        
        self.mock_redis_client.release_lock.assert_called_once()
        self.mock_redis_client.delete_key.assert_called_once_with("task_id") # Still called

if __name__ == '__main__':
    unittest.main()
