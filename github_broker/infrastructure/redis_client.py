import json

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

    def blpop_event(self, queue_name: str, timeout: int = 1) -> str | None:
        """
        指定されたキューからイベントデータをブロッキングで取得します。
        """
        event_data_tuple = self.client.blpop(queue_name, timeout=timeout)
        if event_data_tuple:
            return event_data_tuple[1].decode("utf-8")
        return None

    def set_issue(self, issue_id: str, issue_data: str):
        """
        RedisにIssueデータを設定します。
        このメソッドは、Issue #169 の完了条件の一部として、Issueデータの作成・更新に使用されます。
        """
        self.client.set(f"issue:{issue_id}", issue_data)

    def get_issue(self, issue_id: str) -> str | None:
        """
        RedisからIssueデータを取得します。
        このメソッドは、Issue #169 の完了条件の一部として、Issueデータの取得に使用されます。
        """
        issue_data = self.client.get(f"issue:{issue_id}")
        return issue_data.decode("utf-8") if issue_data else None

    def delete_issue(self, issue_id: str):
        """
        RedisからIssueデータを削除します。
        このメソッドは、Issue #169 の完了条件の一部として、Issueデータの削除に使用されます。
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
                            issues.append(json.loads(issue_data.decode("utf-8")))
                        except json.JSONDecodeError:
                            # 不正なJSONデータは無視するか、ロギングする
                            pass
            if cursor == 0:
                break
        return issues
