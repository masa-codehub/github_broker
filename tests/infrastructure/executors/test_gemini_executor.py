import pytest
from unittest.mock import patch, MagicMock

from github_broker.infrastructure.executors.gemini_executor import GeminiCliExecutor

@pytest.fixture
def executor():
    """Provides a GeminiCliExecutor instance for tests."""
    return GeminiCliExecutor()

@patch('subprocess.Popen')
def test_execute_success(mock_popen, executor):
    """
    Test the successful execution of a task.
    """
    # Arrange
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = ["line 1", "line 2"]
    mock_popen.return_value.__enter__.return_value = mock_proc

    task = {
        "title": "Test Title",
        "body": "Test Body",
        "branch_name": "feature/test"
    }

    # Act
    executor.execute(task)

    # Assert
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    command = args[0]
    assert command[0] == "gemini"
    assert command[1] == "--yolo"
    assert "# Issue: Test Title" in command[3]
    assert "Test Body" in command[3]
    assert "feature/test" in command[3]

@patch('subprocess.Popen')
def test_execute_command_fails(mock_popen, executor):
    """
    Test when the gemini cli command returns a non-zero exit code.
    """
    # Arrange
    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.stdout = ["error occurred"]
    mock_popen.return_value.__enter__.return_value = mock_proc
    task = {"title": "t", "body": "b", "branch_name": "b"}

    # Act
    executor.execute(task)

    # Assert
    mock_popen.assert_called_once()

@patch('subprocess.Popen', side_effect=FileNotFoundError("Command not found"))
def test_execute_file_not_found(mock_popen, executor):
    """
    Test when the gemini cli command is not found.
    """
    # Act
    executor.execute(task={"title": "t", "body": "b", "branch_name": "b"})

    # Assert
    mock_popen.assert_called_once()
