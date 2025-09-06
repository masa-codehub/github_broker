import pytest
import json
from unittest.mock import Mock, patch
from github_broker.application.issue_cache_updater_service import IssueCacheUpdaterService
from github_broker.infrastructure.redis_client import RedisClient

@pytest.fixture
def mock_redis_client():
    return Mock(spec=RedisClient)

@pytest.fixture
def updater_service(mock_redis_client):
    return IssueCacheUpdaterService(redis_client=mock_redis_client)

def test_process_webhook_payload_opened(updater_service, mock_redis_client):
    payload = {
        "action": "opened",
        "issue": {"id": 123, "title": "Test Issue", "body": "This is a test."}
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.set_issue.assert_called_once_with("123", json.dumps(payload["issue"]))
    mock_redis_client.delete_issue.assert_not_called()

def test_process_webhook_payload_edited(updater_service, mock_redis_client):
    payload = {
        "action": "edited",
        "issue": {"id": 456, "title": "Edited Issue", "body": "This is an edited test."}
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.set_issue.assert_called_once_with("456", json.dumps(payload["issue"]))
    mock_redis_client.delete_issue.assert_not_called()

def test_process_webhook_payload_closed(updater_service, mock_redis_client):
    payload = {
        "action": "closed",
        "issue": {"id": 789, "title": "Closed Issue", "body": "This is a closed test."}
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.delete_issue.assert_called_once_with("789")
    mock_redis_client.set_issue.assert_not_called()

def test_process_webhook_payload_reopened(updater_service, mock_redis_client):
    payload = {
        "action": "reopened",
        "issue": {"id": 101, "title": "Reopened Issue", "body": "This is a reopened test."}
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.set_issue.assert_called_once_with("101", json.dumps(payload["issue"]))
    mock_redis_client.delete_issue.assert_not_called()

def test_process_webhook_payload_deleted(updater_service, mock_redis_client):
    payload = {
        "action": "deleted",
        "issue": {"id": 102, "title": "Deleted Issue", "body": "This is a deleted test."}
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.delete_issue.assert_called_once_with("102")
    mock_redis_client.set_issue.assert_not_called()

def test_process_webhook_payload_missing_issue(updater_service, mock_redis_client):
    payload = {
        "action": "opened",
        "no_issue": {}
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.set_issue.assert_not_called()
    mock_redis_client.delete_issue.assert_not_called()

def test_process_webhook_payload_missing_action(updater_service, mock_redis_client):
    payload = {
        "no_action": "opened",
        "issue": {"id": 101, "title": "Missing Action Issue", "body": "This is a test."}
    }
    updater_service._process_webhook_payload(payload)
    mock_redis_client.set_issue.assert_not_called()
    mock_redis_client.delete_issue.assert_not_called()

@patch('github_broker.application.issue_cache_updater_service.logger')
def test_start_stops_when_running_is_false(mock_logger, updater_service, mock_redis_client):
    def lpop_side_effect(*args, **kwargs):
        updater_service.running = False # Set running to False after first call
        return None

    mock_redis_client.lpop_event.side_effect = lpop_side_effect
    updater_service.running = True
    updater_service.start()
    assert not updater_service.running # Should be false after loop exits

@patch('github_broker.application.issue_cache_updater_service.logger')
def test_start_processes_events_and_stops(mock_logger, updater_service, mock_redis_client):
    event1 = json.dumps({"action": "opened", "issue": {"id": 1, "title": "Issue 1"}})
    event2 = json.dumps({"action": "closed", "issue": {"id": 2, "title": "Issue 2"}})

    call_count = 0
    def lpop_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return event1
        elif call_count == 2:
            return event2
        else:
            updater_service.running = False
            return None

    mock_redis_client.lpop_event.side_effect = lpop_side_effect

    updater_service.running = True
    updater_service.start()

    assert mock_redis_client.lpop_event.call_count == 3 # Called for each event + one None
    mock_redis_client.set_issue.assert_called_once_with("1", json.dumps({"id": 1, "title": "Issue 1"}))
    mock_redis_client.delete_issue.assert_called_once_with("2")
    assert not updater_service.running

@patch('github_broker.application.issue_cache_updater_service.logger')
def test_start_handles_json_decode_error(mock_logger, updater_service, mock_redis_client):
    invalid_json = "invalid json"

    call_count = 0
    def lpop_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return invalid_json
        else:
            updater_service.running = False
            return None

    mock_redis_client.lpop_event.side_effect = lpop_side_effect

    updater_service.running = True
    updater_service.start()

    mock_logger.error.assert_called_once()
    assert "Failed to decode JSON payload" in mock_logger.error.call_args[0][0]

@patch('github_broker.application.issue_cache_updater_service.logger')
def test_start_handles_general_exception_during_processing(mock_logger, updater_service, mock_redis_client):
    valid_json = json.dumps({"action": "opened", "issue": {"id": 1, "title": "Issue 1"}})
    updater_service._process_webhook_payload = Mock(side_effect=Exception("Test Error"))

    call_count = 0
    def lpop_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return valid_json
        else:
            updater_service.running = False
            return None

    mock_redis_client.lpop_event.side_effect = lpop_side_effect

    updater_service.running = True
    updater_service.start()

    mock_logger.error.assert_called_once()
    assert "Error processing webhook payload" in mock_logger.error.call_args[0][0]
    assert "Test Error" in mock_logger.error.call_args[0][0]

@patch('github_broker.application.issue_cache_updater_service.logger')
def test_start_moves_payload_to_dlq_on_exception(mock_logger, updater_service, mock_redis_client):
    valid_payload = json.dumps({"action": "opened", "issue": {"id": 1, "title": "Issue 1"}})
    updater_service._process_webhook_payload = Mock(side_effect=Exception("Test Processing Error"))

    call_count = 0
    def lpop_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return valid_payload
        else:
            updater_service.running = False
            return None

    mock_redis_client.lpop_event.side_effect = lpop_side_effect

    updater_service.running = True
    updater_service.start()

    mock_redis_client.rpush_event.assert_called_once_with("webhook_events_dlq", valid_payload)
    mock_logger.error.assert_called_once()
    mock_logger.warning.assert_called_once_with("Webhook payload moved to DLQ: webhook_events_dlq")

def test_stop_sets_running_to_false(updater_service):
    updater_service.running = True
    updater_service.stop()
    assert not updater_service.running
