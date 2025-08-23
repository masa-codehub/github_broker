from unittest.mock import MagicMock

import pytest

from github_broker.infrastructure.redis_client import RedisClient


@pytest.fixture
def mock_redis_instance():
    """redis.Redisインスタンスのモック。"""
    return MagicMock()


@pytest.fixture
def redis_client(mock_redis_instance):
    """モックされたRedisインスタンスを持つRedisClientインスタンス。"""
    return RedisClient(mock_redis_instance)


def test_acquire_lock(redis_client, mock_redis_instance):
    # 準備
    lock_key = "test_lock"
    value = "locked"
    timeout = 300
    mock_redis_instance.set.return_value = True

    # 実行
    result = redis_client.acquire_lock(lock_key, value, timeout)

    # 検証
    mock_redis_instance.set.assert_called_once_with(
        lock_key, value, ex=timeout, nx=True
    )
    assert result is True


def test_release_lock(redis_client, mock_redis_instance):
    # 準備
    lock_key = "test_lock"
    mock_redis_instance.delete.return_value = 1

    # 実行
    result = redis_client.release_lock(lock_key)

    # 検証
    mock_redis_instance.delete.assert_called_once_with(lock_key)
    assert result is True


def test_release_lock_not_found(redis_client, mock_redis_instance):
    # 準備
    lock_key = "test_lock"
    mock_redis_instance.delete.return_value = 0

    # 実行
    result = redis_client.release_lock(lock_key)

    # 検証
    assert result is False


def test_get_value(redis_client, mock_redis_instance):
    # 準備
    key = "test_key"
    value = b"test_value"
    mock_redis_instance.get.return_value = value

    # 実行
    result = redis_client.get_value(key)

    # 検証
    mock_redis_instance.get.assert_called_once_with(key)
    assert result == value.decode("utf-8")


def test_get_value_none(redis_client, mock_redis_instance):
    # 準備
    key = "test_key"
    mock_redis_instance.get.return_value = None

    # 実行
    result = redis_client.get_value(key)

    # 検証
    assert result is None


def test_set_value(redis_client, mock_redis_instance):
    # 準備
    key = "test_key"
    value = "test_value"
    timeout = 300

    # 実行
    redis_client.set_value(key, value, timeout)

    # 検証
    mock_redis_instance.set.assert_called_once_with(key, value, ex=timeout)


def test_delete_key(redis_client, mock_redis_instance):
    # 準備
    key = "test_key"

    # 実行
    redis_client.delete_key(key)

    # 検証
    mock_redis_instance.delete.assert_called_once_with(key)
