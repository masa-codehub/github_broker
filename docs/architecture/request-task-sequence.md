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
    participant GeminiClient as GeminiClient

    Worker->>+ApiServer: POST /request-task (agent_id, capabilities)
    ApiServer->>+TaskService: request_task(agent_id, capabilities)

    loop ロングポーリング (タイムアウトまで)
        TaskService->>+GitHubClient: get_open_issues(repo_name)
        GitHubClient-->>-TaskService: Open Issues List
        TaskService->>TaskService: 1. 役割に合うタスクを候補化 (フィルタリング)
        TaskService->>TaskService: 2. 優先順位付け (最も古いIssueを優先)

        alt 割り当て可能なタスク候補あり
            TaskService->>TaskService: 3. 各候補Issueをチェック
            TaskService->>+RedisClient: acquire_lock(issue_lock_{issue_id}, "locked", timeout=600)
            RedisClient-->>-TaskService: Lock Acquired / Failed

            alt ロック取得成功 & 前提条件(成果物セクション)満たす
                TaskService->>+GitHubClient: update_issue(prev_issue_id, remove_labels=["in-progress", "{agent_id}"], add_labels=["needs-review"])
                GitHubClient-->>-TaskService: OK
                TaskService->>TaskService: GitHub検索インデックス遅延待機 (15秒)

                TaskService->>+GitHubClient: create_branch(branch_name, base_branch)
                GitHubClient-->>-TaskService: OK

                TaskService->>+GitHubClient: update_issue(new_issue_id, add_labels=["in-progress", "{agent_id}"])
                GitHubClient-->>-TaskService: OK

                TaskService->>+GeminiClient: select_best_issue_id(issues, capabilities)
                GeminiClient-->>-TaskService: Selected Issue ID

                TaskService-->>-ApiServer: TaskResponse (issue_id, url, title, body, labels, branch_name, prompt)
                ApiServer-->>-Worker: 200 OK (TaskResponse)
                break
            else ロック取得失敗 または 前提条件満たさない
                TaskService->>TaskService: 次の候補Issueをチェック / リトライ
            end
        else 割り当て可能なタスク候補なし
            TaskService->>TaskService: Wait for retry...
        end
    end
    alt ループ終了後もタスクなし
        TaskService-->>-ApiServer: None
        ApiServer-->>-Worker: 204 No Content
    end
```

## 3. 詳細説明

### 3.1. 主要な登場人物

-   **ワーカーエージェント (Worker):** タスクを要求する外部クライアント。
-   **APIサーバー (ApiServer):** FastAPIで実装されたタスク割り当てのHTTPエンドポイント。
-   **TaskService:** アプリケーションのコアロジックを担うサービス。タスクの選択、割り当て、GitHub操作を調整します。
-   **RedisClient:** Redisとの通信を担当し、主に分散ロックの取得と解放を行います。
-   **GitHubClient:** GitHub APIとの通信を担当し、Issueの取得、ラベルの更新、ブランチの作成などを行います。
-   **GeminiClient:** Gemini APIと連携し、最適なIssueの選択を支援します。

### 3.2. 処理フロー

1.  **タスク要求:** ワーカーエージェントは、自身の`agent_id`と`capabilities`を添えてAPIサーバーの`/request-task`エンドポイントにPOSTリクエストを送信します。
2.  **TaskService呼び出し:** APIサーバーはリクエストを受け取り、`TaskService`の`request_task`メソッドを呼び出します。
3.  **ロングポーリング:** `TaskService`は、割り当て可能なタスクが見つかるまで、またはタイムアウトするまでロングポーリングループに入ります。
    *   **Issueの取得:** `GitHubClient`を介してGitHubからオープンなIssueリストを取得します。
    *   **候補のフィルタリングと優先順位付け:** 取得したIssueリストから、エージェントの`capabilities`に合致するタスクをフィルタリングし、最も古く作成されたIssueを優先します。
    *   **ロック取得:** 優先順位の高い候補Issueに対して、`RedisClient`を使用して分散ロックの取得を試みます。これにより、複数のエージェントが同時に同じIssueを処理することを防ぎます。
    *   **前提条件チェック:** ロック取得に成功した場合、Issueの本文に「成果物」セクションが正しく定義されているかなどの前提条件をチェックします。
    *   **前タスクの完了処理:** もしエージェントに以前の`in-progress`タスクがあれば、そのIssueのラベルを`needs-review`に更新し、`in-progress`と`[agent_id]`ラベルを削除します。GitHubの検索インデックスの遅延を考慮し、一定時間待機します。
    *   **ブランチ作成:** 新しいタスクとして選択されたIssueに対応するブランチを`GitHubClient`を介して作成します。
    *   **タスク割り当て:** 新しいタスクのIssueに`in-progress`と`[agent_id]`ラベルを付与します。
    *   **GeminiによるIssue選択:** `GeminiClient`を呼び出し、利用可能なIssueの中からエージェントの能力に最適なIssueを選択させます。
    *   **レスポンス:** 割り当てられたタスク情報（Issue ID, URL, タイトル, 本文, ラベル, ブランチ名, プロンプト）を`TaskResponse`としてワーカーエージェントに返します。
4.  **タスクなし:** ロングポーリングのループが終了しても割り当て可能なタスクが見つからなかった場合、APIサーバーは`204 No Content`を返します。
