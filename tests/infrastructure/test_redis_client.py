from unittest.mock import MagicMock, call

import pytest

from github_broker.infrastructure.redis_client import RedisClient


@pytest.fixture
def mock_redis_instance():
    """redis.Redisインスタンスのモック。"""
    return MagicMock()


@pytest.fixture
def redis_client(mock_redis_instance):
    """モックされたRedisインスタンスを持つRedisClientインスタンス。"""
    owner = "test_owner"
    repo_name = "test_repo"
    return RedisClient(mock_redis_instance, owner, repo_name)


@pytest.mark.unit
def test_acquire_lock(redis_client, mock_redis_instance):
    # 準備
    lock_key = "test_lock"
    value = "locked"
    timeout = 300
    mock_redis_instance.set.return_value = True

    # 実行
    result = redis_client.acquire_lock(lock_key, value, timeout)

    # 検証
    expected_prefixed_key = "repo::test_owner::test_repo:test_lock"
    mock_redis_instance.set.assert_called_once_with(
        expected_prefixed_key, value, ex=timeout, nx=True
    )
    assert result is True


@pytest.mark.unit
def test_release_lock(redis_client, mock_redis_instance):
    # 準備
    lock_key = "test_lock"
    mock_redis_instance.delete.return_value = 1

    # 実行
    result = redis_client.release_lock(lock_key)

    # 検証
    expected_prefixed_key = "repo::test_owner::test_repo:test_lock"
    mock_redis_instance.delete.assert_called_once_with(expected_prefixed_key)
    assert result is True


@pytest.mark.unit
def test_release_lock_not_found(redis_client, mock_redis_instance):
    # 準備
    lock_key = "test_lock"
    mock_redis_instance.delete.return_value = 0

    # 実行
    result = redis_client.release_lock(lock_key)

    # 検証
    assert result is False


@pytest.mark.unit
def test_get_value(redis_client, mock_redis_instance):
    # 準備
    key = "test_key"
    value = "test_value"  # バイト文字列ではなく通常の文字列を返すように変更
    mock_redis_instance.get.return_value = value

    # 実行
    result = redis_client.get_value(key)

    # 検証
    expected_prefixed_key = "repo::test_owner::test_repo:test_key"
    mock_redis_instance.get.assert_called_once_with(expected_prefixed_key)
    assert result == value  # .decode("utf-8")を削除


@pytest.mark.unit
def test_get_value_none(redis_client, mock_redis_instance):
    # 準備
    key = "test_key"
    mock_redis_instance.get.return_value = None

    # 実行
    result = redis_client.get_value(key)

    # 検証
    assert result is None


@pytest.mark.unit
def test_set_value(redis_client, mock_redis_instance):
    # 準備
    key = "test_key"
    value = "test_value"
    timeout = 300

    # 実行
    redis_client.set_value(key, value, timeout)

    # 検証
    expected_prefixed_key = "repo::test_owner::test_repo:test_key"
    mock_redis_instance.set.assert_called_once_with(
        expected_prefixed_key, value, ex=timeout
    )


@pytest.mark.unit
def test_delete_key(redis_client, mock_redis_instance):
    # 準備
    key = "test_key"

    # 実行
    redis_client.delete_key(key)

    # 検証
    expected_prefixed_key = "repo::test_owner::test_repo:test_key"
    mock_redis_instance.delete.assert_called_once_with(expected_prefixed_key)


@pytest.mark.unit
def test_get_keys_by_pattern(redis_client, mock_redis_instance):
    # 準備
    pattern = "issue:*"
    prefixed_pattern = "repo::test_owner::test_repo:issue:*"
    found_keys = [
        "repo::test_owner::test_repo:issue:1",
        "repo::test_owner::test_repo:issue:2",
    ]
    # `decode_responses=True` のため、scanは文字列を返す
    mock_redis_instance.scan.side_effect = [
        (1, found_keys[:1]),
        (0, found_keys[1:]),
    ]

    # 実行
    result = redis_client.get_keys_by_pattern(pattern)

    # 検証
    assert mock_redis_instance.scan.call_args_list == [
        call(0, match=prefixed_pattern),
        call(1, match=prefixed_pattern),
    ]
    assert result == ["issue:1", "issue:2"]
