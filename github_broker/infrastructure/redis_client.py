import redis


class RedisClient:
    """
    Redisクライアント。分散ロックに使用されます。
    """

    def __init__(self, redis_instance: redis.Redis):
        self.client = redis_instance

    def acquire_lock(self, lock_key, value, timeout=600) -> bool:
        """
        ロックを取得します。
        """
        # nx=Trueは、キーがまだ存在しない場合にのみ設定されることを保証します。
        return self.client.set(lock_key, value, ex=timeout, nx=True)

    def release_lock(self, lock_key) -> bool:
        """
        ロックを解放します。
        """
        # キーを削除することでロックが解放されます。
        return self.client.delete(lock_key) > 0

    def get_value(self, key) -> str | None:
        """
        Redisから値を取得します。
        """
        value = self.client.get(key)
        return value.decode("utf-8") if value else None

    def set_value(self, key, value, timeout=600):
        """
        Redisに値を設定します。
        """
        self.client.set(key, value, ex=timeout)

    def delete_key(self, key):
        """
        Redisからキーを削除します。
        """
        self.client.delete(key)
