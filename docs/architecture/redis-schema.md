# Redisキースキーマ 設計書

## 1. 概要

このドキュメントは、`github_broker`プロジェクトにおけるRedisの利用方法、特にキーの命名規則と構造（スキーマ）について説明します。

本プロジェクトでは、Redisを主に**分散ロック**のメカニズムと**遅延タスク管理**に利用しています。これにより、複数のエージェントが同時にタスク割り当てを要求した場合でも、単一のIssueが複数のエージェントに割り当てられてしまうといった競合状態を防ぎ、また、レビューIssueの割り当てに意図的な遅延を設けることを可能にします。

## 2. キーの命名規則と構造

### 2.1. Issueロックキー

- **キーのフォーマット:** `issue_lock_{issue_id}`
- **説明:** 特定のIssueが現在処理中（割り当て候補としてロックされている状態）であることを示すためのキーです。
- **例:** Issue番号が `123` の場合、キーは `issue_lock_123` となります。

### 2.2. 値

- **値:** `locked`
- **説明:** キーが存在する場合、その値は常に文字列 `locked` となります。値自体に意味はなく、キーの存在がロックされていることを示します。

### 2.3. 有効期限 (Timeout)

- **TTL:** 600秒 (10分)
- **説明:** ロック取得時に、キーには必ず有効期限（Time To Live）が設定されます。これは、タスクの割り当て処理中に万が一サーバーがクラッシュした場合でも、ロックが永久に残り続けてしまう**デッドロック**状態を防ぐための重要な仕組みです。10分という時間は、GitHub APIの応答遅延や予期せぬリトライ処理なども考慮し、タスク割り当てプロセスが完了するまでの時間として十分に安全な上限値として設定されています。有効期限が切れると、キーはRedisから自動的に削除され、ロックは解放されます。

### 2.4. レビュー遅延管理キー (Review Delay Management Key)

レビューIssueが検出されてから実際にエージェントに割り当てられるまでの遅延（タイムアウト）を管理するためのキーです。

- **キーのフォーマット:** `review_delay_{issue_id}`
- **データ型:** Hash
- **説明:** `TaskService`が`needs-review`ラベルの付いたIssueを検出した際に作成されます。このキーの存在と値により、遅延時間が経過したかどうかを判断します。
- **フィールド:**
    - **`found_at` (String):** Issueが最初に検出された時刻（ISO 8601形式）。この時刻と設定された遅延時間（例: 5分）を比較し、タスク割り当ての可否を判断します。
    - **`pr_number` (String):** 関連するPull Requestの番号。
    - **`status` (String):** 遅延処理の状態。例: `PENDING`, `READY_FOR_ASSIGNMENT`。
- **有効期限 (TTL):** 86400秒 (24時間)
- **例:** Issue番号が `1582` の場合、キーは `review_delay_1582` となり、値は以下のようになります。

```json
{
  "found_at": "2025-10-21T10:00:00Z",
  "pr_number": "1583",
  "status": "PENDING"
}
```

## 3. 利用フロー

Redisのロック機能は、`TaskService`内の `_find_first_assignable_task` メソッドで利用されています。

1.  **ロック取得:**
    - 割り当て可能なIssueが見つかると、`redis_client.acquire_lock()` を呼び出します。
    - このメソッドは内部でRedisの `SETNX` (SET if Not eXists) コマンドを実行し、キーが存在しない場合にのみキーと値、そして有効期限を設定します。
    - `SETNX`はアトミックな操作であるため、複数のプロセスが同時に実行しても競合は発生しません。

2.  **処理の実行:**
    - ロックの取得に成功した場合、GitHub APIを呼び出してIssueにラベルを付与し、ブランチを作成するなどの割り当て処理を実行します。

3.  **ロック解放:**
    - 割り当て処理が正常に完了しなかった場合（エラー発生時など）は、`redis_client.release_lock()` を呼び出して明示的にキーを削除し、ロックを解放します。
    - 正常に完了した場合は、他のエージェントが同じIssueを処理する必要はないため、ロックは有効期限まで保持されます。

```python
# /github_broker/application/task_service.py (抜粋)

# ...
            lock_key = f"issue_lock_{task.issue_id}"
            if not self.redis_client.acquire_lock(lock_key, "locked", timeout=600):
                logger.warning(
                    f"Issue #{task.issue_id} is locked by another agent. Skipping."
                )
                continue

            try:
                # ... 割り当て処理 ...
            except Exception as e:
                # ... エラー処理 ...
                self.redis_client.release_lock(lock_key)
                raise
# ...
```