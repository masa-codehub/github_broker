import json

import redis


class RedisClient:
    """
    Redisクライアント。分散ロックに使用されます。
    """

    def __init__(self, redis_instance: redis.Redis):
        self.client = redis_instance

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

    def rpush_event(self, queue_name: str, event_data: str) -> None:
        """
        指定されたキューにイベントデータを追加します。
        """
        self.client.rpush(queue_name, event_data)

    def lpop_event(self, queue_name: str) -> str | None:
        """
        指定されたキューからイベントデータを取得します。
        """
        return self.client.lpop(queue_name)

    def blpop_event(self, queue_name: str, timeout: int = 1) -> str | None:
        """
        指定されたキューからイベントデータをブロッキングで取得します。
        """
        event_data_tuple = self.client.blpop(queue_name, timeout=timeout)
        if event_data_tuple:
            return event_data_tuple[1]
        return None

    def set_issue(self, issue_id: str, issue_data: str) -> None:
        """
        RedisにIssueデータを設定します。
        """
        self.client.set(f"issue:{issue_id}", issue_data)

    def get_issue(self, issue_id: str) -> str | None:
        """
        RedisからIssueデータを取得します。
        """
        return self.client.get(f"issue:{issue_id}")

    def delete_issue(self, issue_id: str) -> None:
        """
        RedisからIssueデータを削除します。
        """
        self.client.delete(f"issue:{issue_id}")

    def get_all_issues(self) -> list[dict]:
        """
        Redisに保存されているすべてのIssueデータを取得します。
        """
        issues = []
        cursor = 0
        while True:
            cursor, keys = self.client.scan(cursor, match="issue:*", count=100)
            if keys:
                issue_data_list = self.client.mget(keys)
                for issue_data in issue_data_list:
                    if issue_data:
                        try:
                            issues.append(json.loads(issue_data))
                        except json.JSONDecodeError:
                            pass
            if cursor == 0:
                break
        return issues
