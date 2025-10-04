# APIエンドポイント `/request-task` 詳細シーケンス図

## 1. 概要

このドキュメントは、ワーカーエージェントがタスクを要求する際の `/api/v1/request-task` エンドポイントの内部処理フローを詳細なシーケンス図で示します。これにより、タスクの選択、ロック、割り当て、および関連するGitHub操作の動的な振る舞いを明確にします。

## 2. シーケンス図

```mermaid
sequenceDiagram
    participant Worker as ワーカーエージェント
    participant ApiServer as APIサーバー (FastAPI)
    participant TaskService as TaskService
    participant RedisClient as RedisClient
    participant GitHubClient as GitHubClient

    Worker->>+ApiServer: POST /request-task (agent_id, agent_role)
    ApiServer->>+TaskService: request_task(agent_id, agent_role)

    TaskService->>+RedisClient: get_value(OPEN_ISSUES_CACHE_KEY)
    RedisClient-->>-TaskService: Cached Issues List

    alt 前タスク(in-progress)がRedisに記録されている or GitHub上で見つかる
        Note over TaskService: prev_issue_id は agent_id に以前割り当てられていた Issue の ID
        TaskService->>+GitHubClient: update_issue(prev_issue_id, remove_labels=["in-progress", "{agent_id}"], add_labels=["needs-review"])
        GitHubClient-->>-TaskService: OK
    end

    TaskService->>TaskService: 1. 役割に合うタスクを候補化 (フィルタリング)
    Note over TaskService: フィルタリング条件:
    Note over TaskService: - エージェントの役割に合致
    Note over TaskService: - `in-progress` ラベルが付いていない
    Note over TaskService: - `needs-review` ラベルが付いている場合、レビューコメント待機時間（例: 24時間）が経過している
    
    alt 割り当て可能なタスク候補あり
        Note over TaskService: 優先順位に基づき最初の候補を選択 (selected_issue_id)
        Note over TaskService: 優先順位の考慮事項:
        Note over TaskService: - `priority-high` > `priority-medium` > `priority-low`
        Note over TaskService: - 同一優先度内では作成日時が古いもの
        TaskService->>+RedisClient: acquire_lock(issue_lock_{selected_issue_id}, "locked", timeout=600)
        RedisClient-->>-TaskService: Lock Acquired / Failed

        alt ロック取得成功 & 前提条件(成果物セクション)満たす
            TaskService->>+GitHubClient: create_branch(branch_name, base_branch)
            GitHubClient-->>-TaskService: OK

            TaskService->>+GitHubClient: update_issue(selected_issue_id, add_labels=["in-progress", "{agent_id}"])
            GitHubClient-->>-TaskService: OK

            TaskService->>+RedisClient: set_value(agent_current_task:{agent_id}, selected_issue_id)
            RedisClient-->>-TaskService: OK

            TaskService-->>-ApiServer: TaskResponse (issue_id, url, title, body, labels, branch_name, prompt)
            ApiServer-->>-Worker: 200 OK (TaskResponse)
        else ロック取得失敗 または 前提条件満たさない
            TaskService->>TaskService: 次の候補Issueをチェック / リトライ
        end
    else 割り当て可能なタスク候補なし
        TaskService-->>-ApiServer: None
        ApiServer-->>-Worker: 204 No Content
    end
```

## 3. 詳細説明

### 3.1. 主要な登場人物

-   **ワーカーエージェント (Worker):** タスクを要求する外部クライアント。
-   **APIサーバー (ApiServer):** FastAPIで実装されたタスク割り当てのHTTPエンドポイント。
-   **TaskService:** アプリケーションのコアロジックを担うサービス。タスクの選択、割り当て、GitHub操作を調整します。
-   **RedisClient:** Redisとの通信を担当し、Issueのキャッシュ読み取りや分散ロックの取得・解放を行います。
-   **GitHubClient:** GitHub APIとの通信を担当し、Issueの取得、ラベルの更新、ブランチの作成などを行います。

### 3.2. 処理フロー

1.  **タスク要求:** ワーカーエージェントは、自身の`agent_id`と`agent_role`を添えてAPIサーバーの`/request-task`エンドポイントにPOSTリクエストを送信します。
2.  **TaskService呼び出し:** APIサーバーはリクエストを受け取り、`TaskService`の`request_task`メソッドを呼び出します。
3.  **Issueキャッシュの取得:** `TaskService`は、まず`RedisClient`を介して、バックグラウンドで定期的にキャッシュされているオープンなIssueのリストを取得します。
4.  **前タスクの完了処理:** エージェントに以前割り当てられていた`in-progress`状態のタスク(`prev_issue_id`)がないか確認します。もし存在すれば、そのIssueのラベルを`needs-review`に更新し、`in-progress`と`[agent_id]`ラベルを削除します。
5.  **タスク候補の選定:**
    *   **候補のフィルタリング:** Redisから取得したIssueリストから、以下の条件を満たすタスクをフィルタリングします。
        *   エージェントの`agent_role`に合致する。
        *   `in-progress`ラベルが付いていない。
        *   `needs-review`ラベルが付いている場合、そのIssueが`needs-review`ラベルを付与されてから一定時間（例: 24時間）が経過していることを確認します。これは、ポーリング時にIssueの`updated_at`タイムスタンプと現在の時刻を比較することで実現されます。
    *   **最適Issue選択:** フィルタリングされた候補Issueが存在する場合、`TaskService`は以下の優先順位に基づき、最適なIssueを選択します (`selected_issue_id`)。
        *   **優先度ラベル:** `priority-high` > `priority-medium` > `priority-low` の順に優先します。
        *   **作成日時:** 同一優先度内では、作成日時が最も古いIssueを優先します。
    *   **ロック取得:** 選択されたIssue (`selected_issue_id`) に対して、`RedisClient`を使用して分散ロックの取得を試みます。これにより、複数のエージェントが同時に同じIssueを処理することを防ぎます。
    *   **前提条件チェック:** ロック取得に成功した場合、Issueの本文に「成果物」セクションが正しく定義されているかなどの前提条件をチェックします。
6.  **タスク割り当てとレスポンス:**
    *   **ブランチ作成:** 新しいタスクとして選択されたIssueに対応するブランチを`GitHubClient`を介して作成します。
    *   **タスク割り当て:** 新しいタスクのIssueに`in-progress`と`[agent_id]`ラベルを付与します。
    *   **現在タスクの記録:** `RedisClient`に、エージェントが現在どのIssueに取り組んでいるか (`agent_current_task:{agent_id}`) を記録します。
    *   **レスポンス:** 割り当てられたタスク情報（Issue ID, URL, タイトル, 本文, ラベル, ブランチ名, プロンプト）を`TaskResponse`としてワーカーエージェントに返します。
7.  **タスクなし:** 割り当て可能なタスクが見つからなかった場合、APIサーバーは`204 No Content`を返します。