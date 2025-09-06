import json
from unittest.mock import Mock, patch

import pytest

from github_broker.application.issue_cache_updater_service import (
    IssueCacheUpdaterService,
)
from github_broker.infrastructure.redis_client import RedisClient


@pytest.fixture
def mock_redis_client():
    """Mock RedisClient."""
    return Mock(spec=RedisClient)


@pytest.fixture
def updater_service(mock_redis_client):
    """Fixture for IssueCacheUpdaterService."""
    return IssueCacheUpdaterService(redis_client=mock_redis_client)


def test_process_webhook_payload_opened(updater_service, mock_redis_client):
    """Test processing of 'opened' webhook payload."""
    payload = {
        "action": "opened",
        "issue": {"id": 123, "title": "Test Issue", "body": "This is a test."},
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.set_issue.assert_called_once_with(
        "123", json.dumps(payload["issue"])
    )
    mock_redis_client.delete_issue.assert_not_called()


def test_process_webhook_payload_edited(updater_service, mock_redis_client):
    """Test processing of 'edited' webhook payload."""
    payload = {
        "action": "edited",
        "issue": {
            "id": 456,
            "title": "Edited Issue",
            "body": "This is an edited test.",
        },
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.set_issue.assert_called_once_with(
        "456", json.dumps(payload["issue"])
    )
    mock_redis_client.delete_issue.assert_not_called()


def test_process_webhook_payload_closed(updater_service, mock_redis_client):
    """Test processing of 'closed' webhook payload."""
    payload = {
        "action": "closed",
        "issue": {"id": 789, "title": "Closed Issue", "body": "This is a closed test."},
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.delete_issue.assert_called_once_with("789")
    mock_redis_client.set_issue.assert_not_called()


def test_process_webhook_payload_reopened(updater_service, mock_redis_client):
    """Test processing of 'reopened' webhook payload."""
    payload = {
        "action": "reopened",
        "issue": {
            "id": 101,
            "title": "Reopened Issue",
            "body": "This is a reopened test.",
        },
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.set_issue.assert_called_once_with(
        "101", json.dumps(payload["issue"])
    )
    mock_redis_client.delete_issue.assert_not_called()


def test_process_webhook_payload_deleted(updater_service, mock_redis_client):
    """Test processing of 'deleted' webhook payload."""
    payload = {
        "action": "deleted",
        "issue": {
            "id": 102,
            "title": "Deleted Issue",
            "body": "This is a deleted test.",
        },
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.delete_issue.assert_called_once_with("102")
    mock_redis_client.set_issue.assert_not_called()


def test_process_webhook_payload_missing_issue(updater_service, mock_redis_client):
    """Test that payload with missing 'issue' is ignored."""
    payload = {"action": "opened"}
    updater_service._process_webhook_payload(payload)
    mock_redis_client.set_issue.assert_not_called()
    mock_redis_client.delete_issue.assert_not_called()


def test_process_webhook_payload_missing_action(updater_service, mock_redis_client):
    """Test that payload with missing 'action' is ignored."""
    payload = {"issue": {"id": 101}}
    updater_service._process_webhook_payload(payload)
    mock_redis_client.set_issue.assert_not_called()
    mock_redis_client.delete_issue.assert_not_called()


@patch("github_broker.application.issue_cache_updater_service.logger")
def test_process_payload_handles_json_decode_error(
    mock_logger, updater_service, mock_redis_client
):
    """Test that JSON decoding errors are caught and logged."""
    invalid_json = "invalid json"
    updater_service._process_payload(invalid_json)
    mock_logger.error.assert_called_once()
    assert "Failed to decode JSON payload" in mock_logger.error.call_args[0][0]


@patch("github_broker.application.issue_cache_updater_service.logger")
def test_process_payload_moves_to_dlq_on_exception(
    mock_logger, updater_service, mock_redis_client
):
    """Test that payloads causing exceptions are moved to the DLQ."""
    valid_payload = json.dumps({"action": "opened", "issue": {"id": 1}})
    updater_service._process_webhook_payload = Mock(side_effect=Exception("Test Error"))

    updater_service._process_payload(valid_payload)

    mock_redis_client.rpush_event.assert_called_once_with(
        "webhook_events_dlq", valid_payload
    )
    mock_logger.warning.assert_called_once_with(
        "Webhook payload moved to DLQ: webhook_events_dlq"
    )


def test_stop_clears_running_event(updater_service):
    """Test that stop() clears the running event."""
    updater_service._running.set()
    updater_service.stop()
    assert not updater_service.is_running()


@patch("threading.Thread")
def test_start_creates_and_starts_thread(mock_thread, updater_service):
    """Test that start() creates and starts a new thread."""
    updater_service.start()
    mock_thread.assert_called_once_with(target=updater_service._run_loop, daemon=True)
    updater_service._thread.start.assert_called_once()
    assert updater_service.is_running()


def test_start_does_not_start_if_already_running(updater_service):
    """Test that start() does nothing if the service is already running."""
    updater_service._running.set()
    updater_service._thread = Mock()
    updater_service.start()
    updater_service._thread.start.assert_not_called()
