import redis


class RedisClient:
    """
    Redisクライアント。分散ロックに使用されます。
    """

    def __init__(self, redis: redis.Redis):
        self.client = redis

    def acquire_lock(self, lock_key: str, value: str, timeout: int = 600) -> bool:
        """
        ロックを取得します。
        """
        # nx=Trueは、キーがまだ存在しない場合にのみ設定されることを保証します。
        result = self.client.set(lock_key, value, ex=timeout, nx=True)
        return result if result is not None else False

    def release_lock(self, lock_key: str) -> bool:
        """
        ロックを解放します。
        """
        # キーを削除することでロックが解放されます。
        return self.client.delete(lock_key) > 0

    def get_value(self, key: str) -> str | None:
        """
        Redisから値を取得します。
        """
        return self.client.get(key)

    def set_value(self, key: str, value: str, timeout: int = 600) -> None:
        """
        Redisに値を設定します。
        """
        self.client.set(key, value, ex=timeout)

    def delete_key(self, key: str) -> None:
        """
        Redisからキーを削除します。
        """
        self.client.delete(key)
