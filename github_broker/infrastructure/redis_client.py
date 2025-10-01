import redis
from urllib.parse import quote


class RedisClient:
    """
    Redisクライアント。分散ロックに使用されます。
    """

    def __init__(self, redis: redis.Redis, owner: str, repo_name: str):
        self.client = redis
        self.owner = owner
        self.repo_name = repo_name

    def _get_prefixed_key(self, key: str) -> str:
        """
        キーにリポジトリプレフィックスを付与します。
        """
        encoded_owner = quote(self.owner, safe='')
        encoded_repo_name = quote(self.repo_name, safe='')
        return f"repo_{encoded_owner}_{encoded_repo_name}:{key}"

    def acquire_lock(self, lock_key: str, value: str, timeout: int = 600) -> bool:
        """
        ロックを取得します。
        """
        prefixed_lock_key = self._get_prefixed_key(lock_key)
        # nx=Trueは、キーがまだ存在しない場合にのみ設定されることを保証します。
        result = self.client.set(prefixed_lock_key, value, ex=timeout, nx=True)
        return result if result is not None else False

    def release_lock(self, lock_key: str) -> bool:
        """
        ロックを解放します。
        """
        prefixed_lock_key = self._get_prefixed_key(lock_key)
        # キーを削除することでロックが解放されます。
        return self.client.delete(prefixed_lock_key) > 0

    def get_value(self, key: str) -> str | None:
        """
        Redisから値を取得します。
        """
        prefixed_key = self._get_prefixed_key(key)
        return self.client.get(prefixed_key)

    def set_value(self, key: str, value: str, timeout: int = 600) -> None:
        """
        Redisに値を設定します。
        """
        prefixed_key = self._get_prefixed_key(key)
        self.client.set(prefixed_key, value, ex=timeout)

    def delete_key(self, key: str) -> None:
        """
        Redisからキーを削除します。
        """
        prefixed_key = self._get_prefixed_key(key)
        self.client.delete(prefixed_key)
