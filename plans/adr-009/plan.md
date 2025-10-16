# 計画: ADR-009 ロングポーリングの廃止

## 1. Epic: `ロングポーリング方式の廃止とシンプルポーリングへの切り替え`
- **目的:** ADR-009で決定されたアーキテクチャ変更を実装する。
- **完了条件:** ADR-009に記載された3つの検証基準をすべて満たすこと。
- **ブランチ戦略:**
    - **ベースブランチ:** `main`
    - **作業ブランチ:** `feature/deprecate-long-polling`
- **ステータス:** `Not Created`

## 2. Story: `TaskServiceのポーリングロジックを即時応答に修正`
- **目的:** `TaskService`からロングポーリングのロジックを削除し、関連するテストを修正する。
- **As-is:** `request_task`メソッドは、タスクがない場合にクライアントを待機させる。
- **To-be:** `request_task`メソッドは、タスクがない場合に即座に`None`を返す。
- **完了条件:**
    - `task_service.py`からロングポーリングのコードが削除されている。
    - `test_task_service.py`に、タスクがない場合に即時`None`が返ることを検証するテストが追加・修正され、パスする。
- **成果物:**
    - `github_broker/application/task_service.py`
    - `tests/application/test_task_service.py`
- **担当エージェント:** `BACKENDCODER`
- **優先度:** `P1`
- **ステータス:** `Not Created`

---
### **実装の詳細指示 (For BACKENDCODER)**

#### **ファイル: `github_broker/application/task_service.py`**

1.  **`async def request_task(...)` メソッドを修正してください。**
    - メソッド内にある、ロングポーリングを実現している `while True:` ループ、および関連する時間計算（`start_time`, `elapsed_time`など）、`asyncio.sleep(wait_time)` をすべて削除します。
    - メソッドの冒頭で `_check_for_available_task` を呼び出し、タスクを一度だけチェックする処理は残します。
    - `_check_for_available_task` の結果が `None` だった場合、ログを出力し、即座に `None` を返してメソッドを終了するようにしてください。

#### **ファイル: `tests/application/test_task_service.py`**

1.  **`request_task` のためのテストを修正・追加してください。**
    - `RedisClient` や `GitHubClient` をモックし、割り当て可能なタスクが一つも存在しない状態をセットアップします。
    - その状態で `task_service.request_task()` を呼び出します。
    - 呼び出しが即座に完了し（`asyncio.sleep`などが呼ばれないこと）、戻り値が `None` であることをアサートするテストケースを追加してください。
---
