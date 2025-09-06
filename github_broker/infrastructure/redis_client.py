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

    def rpush_event(self, queue_name: str, event_data: str):
        """
        指定されたキューにイベントデータを追加します。
        """
        self.client.rpush(queue_name, event_data)

    def lpop_event(self, queue_name: str) -> str | None:
        """
        指定されたキューからイベントデータを取得します。
        """
        event_data = self.client.lpop(queue_name)
        return event_data.decode("utf-8") if event_data else None

    def set_issue(self, issue_id: str, issue_data: str):
        """
        RedisにIssueデータを設定します。
        """
        self.client.set(f"issue:{issue_id}", issue_data)

    def get_issue(self, issue_id: str) -> str | None:
        """
        RedisからIssueデータを取得します。
        """
        issue_data = self.client.get(f"issue:{issue_id}")
        return issue_data.decode("utf-8") if issue_data else None

    def delete_issue(self, issue_id: str):
        """
        RedisからIssueデータを削除します。
        """
        self.client.delete(f"issue:{issue_id}")

    def get_all_issues(self) -> list[str]:
        """
        Redisに保存されているすべてのIssueデータを取得します。
        """
        issue_keys = self.client.keys("issue:*")
        issues = []
        for key in issue_keys:
            issue_data = self.client.get(key)
            if issue_data:
                issues.append(issue_data.decode("utf-8"))
        return issues
