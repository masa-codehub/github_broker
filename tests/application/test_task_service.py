
import unittest
from unittest.mock import patch, MagicMock

from github_broker.application.task_service import TaskService
from github_broker.interface.models import TaskResponse

class TestTaskService(unittest.TestCase):

    def setUp(self):
        """Set up mock clients for TaskService."""
        self.mock_github_client = MagicMock()
        self.mock_redis_client = MagicMock()
        self.repo_name = "test/repo"
        self.task_service = TaskService(
            github_client=self.mock_github_client,
            redis_client=self.mock_redis_client,
            repo_name=self.repo_name
        )

    def test_request_task_success_first_task(self):
        """
        Test the successful assignment of a task to an agent with no previous task.
        """
        # Arrange
        agent_id = "test-agent-001"
        capabilities = ["python", "fastapi"]

        # --- Mock Redis Client responses ---
        self.mock_redis_client.acquire_lock.return_value = True
        self.mock_redis_client.get_assignment.return_value = None # No previous task

        # --- Mock GitHub Client responses ---
        mock_issue = MagicMock()
        mock_issue.id = 123
        mock_issue.number = 123
        mock_issue.title = "Fix the bug"
        mock_issue.body = "There is a bug that needs fixing."
        mock_label = MagicMock()
        mock_label.name = "bug"
        mock_issue.labels = [mock_label]
        mock_issue.html_url = "https://github.com/test/repo/issues/123"
        self.mock_github_client.get_open_issues.return_value = [mock_issue]
        self.mock_github_client.create_branch.return_value = True

        # Act
        result = self.task_service.request_task(agent_id, capabilities)

        # Assert
        # --- Verify lock handling ---
        self.mock_redis_client.acquire_lock.assert_called_once()
        self.mock_redis_client.release_lock.assert_called_once()

        # --- Verify previous task handling ---
        self.mock_redis_client.get_assignment.assert_called_once_with(agent_id)
        # No previous task, so label should not be updated
        self.mock_github_client.update_issue_label.assert_not_called()

        # --- Verify new task assignment ---
        self.mock_github_client.get_open_issues.assert_called_once()
        # TODO: Make repo_name configurable
        # self.mock_github_client.get_open_issues.assert_called_once_with(repo_name=repo_name)
        
        # --- Verify branch creation ---
        expected_branch_name = f"feature/issue-{mock_issue.id}"
        self.mock_github_client.create_branch.assert_called_once_with(
            repo_name=self.repo_name,
            branch_name=expected_branch_name
        )

        # --- Verify ledger update ---
        self.mock_redis_client.set_assignment.assert_called_once_with(agent_id, mock_issue.id)

        # --- Verify response ---
        self.assertIsInstance(result, TaskResponse)
        self.assertEqual(result.issue_id, mock_issue.id)
        self.assertEqual(result.title, mock_issue.title)
        self.assertEqual(result.branch_name, expected_branch_name)

    def test_request_task_no_issues_available(self):
        """
        Test that no task is assigned when no open issues are available.
        """
        # Arrange
        agent_id = "test-agent-002"
        capabilities = ["react", "frontend"]
        self.mock_redis_client.acquire_lock.return_value = True
        self.mock_redis_client.get_assignment.return_value = None
        self.mock_github_client.get_open_issues.return_value = [] # No issues

        # Act
        result = self.task_service.request_task(agent_id, capabilities)

        # Assert
        self.assertIsNone(result)
        self.mock_redis_client.acquire_lock.assert_called_once()
        self.mock_github_client.get_open_issues.assert_called_once()
        # Should not proceed to create branch or assign task
        self.mock_github_client.create_branch.assert_not_called()
        self.mock_redis_client.set_assignment.assert_not_called()
        # Lock should always be released
        self.mock_redis_client.release_lock.assert_called_once()

    def test_request_task_with_previous_task(self):
        """
        Test that a previous task is marked as complete before assigning a new one.
        """
        # Arrange
        agent_id = "test-agent-003"
        capabilities = ["python"]
        previous_issue_id = 999

        self.mock_redis_client.acquire_lock.return_value = True
        self.mock_redis_client.get_assignment.return_value = previous_issue_id

        # Mock for the new issue to be assigned
        new_mock_issue = MagicMock()
        new_mock_issue.id = 124
        new_mock_issue.number = 124
        new_mock_issue.title = "A new task"
        new_mock_issue.body = "Details for the new task."
        new_mock_issue.labels = []
        new_mock_issue.html_url = "https://github.com/test/repo/issues/124"
        self.mock_github_client.get_open_issues.return_value = [new_mock_issue]

        # Act
        result = self.task_service.request_task(agent_id, capabilities)

        # Assert
        # --- Verify previous task handling ---
        self.mock_redis_client.get_assignment.assert_called_once_with(agent_id)
        self.mock_github_client.update_issue_label.assert_called_once_with(
            repo_name=self.repo_name,
            issue_id=previous_issue_id,
            new_label="needs-review"
        )

        # --- Verify new task assignment is still correct ---
        self.assertIsNotNone(result)
        self.assertEqual(result.issue_id, new_mock_issue.id)
        self.mock_redis_client.set_assignment.assert_called_once_with(agent_id, new_mock_issue.id)
        self.mock_github_client.create_branch.assert_called_once()
        self.mock_redis_client.release_lock.assert_called_once()

    def test_request_task_lock_fails(self):
        """
        Test that an exception is raised if the lock cannot be acquired.
        """
        # Arrange
        agent_id = "test-agent-004"
        capabilities = ["*"]
        self.mock_redis_client.acquire_lock.return_value = False

        # Act & Assert
        with self.assertRaisesRegex(Exception, "Server is busy. Please try again later."):
            self.task_service.request_task(agent_id, capabilities)

        # Verify that no other operations were attempted
        self.mock_redis_client.get_assignment.assert_not_called()
        self.mock_github_client.get_open_issues.assert_not_called()
        self.mock_redis_client.release_lock.assert_not_called()

if __name__ == '__main__':
    unittest.main()
