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
    participant GeminiExecutor as GeminiExecutor

    Worker->>+ApiServer: POST /request-task (agent_id)
    ApiServer->>+TaskService: request_task(agent_id)

    Note over TaskService: 最初のタスクチェック (is_first_check=True)
    TaskService->>TaskService: _check_for_available_task()

    alt 前タスク(in-progress)が見つかる
        TaskService->>+GitHubClient: update_issue(prev_issue_id, remove_labels=["in-progress", "{agent_id}"], add_labels=["needs-review"])
        GitHubClient-->>-TaskService: OK
    end

    TaskService->>+RedisClient: get_value("open_issues")
    RedisClient-->>-TaskService: Cached Issues List
    TaskService->>TaskService: 役割に合うタスクを候補化

    alt 割り当て可能なタスク候補あり
        TaskService->>TaskService: 候補IssueをIssue番号順にソート
        TaskService->>+RedisClient: acquire_lock(issue_lock_{issue_id})
        RedisClient-->>-TaskService: Lock Acquired
        
        TaskService->>+GitHubClient: create_branch(branch_name)
        GitHubClient-->>-TaskService: OK
        TaskService->>+GitHubClient: add_label(issue_id, ["in-progress", "{agent_id}"])
        GitHubClient-->>-TaskService: OK

        TaskService->>+GeminiExecutor: build_prompt(issue_url, branch_name)
        GeminiExecutor-->>-TaskService: prompt_string

        TaskService->>+RedisClient: set_value(agent_current_task:{agent_id}, {issue_id})
        RedisClient-->>-TaskService: OK

        TaskService-->>-ApiServer: TaskResponse
        ApiServer-->>-Worker: 200 OK (TaskResponse)

    else 割り当て可能なタスク候補なし (ロングポーリング開始)
        loop Long Polling (timeoutまで)
            ApiServer->>TaskService: asyncio.sleep(interval)
            Note over TaskService: 次のタスクチェック (is_first_check=False)
            TaskService->>TaskService: _check_for_available_task()
            
            alt タスクが見つかる
                TaskService-->>-ApiServer: TaskResponse
                ApiServer-->>-Worker: 200 OK (TaskResponse)
                break
            end
        end
        
        alt タイムアウト
            TaskService-->>-ApiServer: None
            ApiServer-->>-Worker: 204 No Content
        end
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

1.  **タスク要求とロングポーリング:** ワーカーエージェントは、自身の`agent_id`を添えてAPIサーバーの`/request-task`エンドポイントにPOSTリクエストを送信します。サーバーはリクエストを受け取ると`TaskService`の`request_task`メソッドを呼び出します。このメソッドはロングポーリングで動作し、割り当て可能なタスクが見つからない場合は、指定されたタイムアウト時間までタスクの出現を待ち続けます。

2.  **初回タスクチェック:** `request_task`は、まず内部的に`_check_for_available_task(is_first_check=True)`を呼び出します。これが最初のチェックであることを示します。

3.  **前タスクの完了処理:** `is_first_check`が`True`の場合のみ、エージェントに以前割り当てられていた`in-progress`状態のタスクがないか検索します。もし存在すれば、そのIssueのラベルを`needs-review`に更新し、`in-progress`と`[agent_id]`ラベルを削除します。

4.  **タスク候補の選定:**
    *   **キャッシュ取得:** `RedisClient`を介して、バックグラウンドで定期的にキャッシュされているオープンなIssueのリスト (`open_issues`) を取得します。
    *   **候補フィルタリング:** Redisから取得したIssueリストから、エージェントの`agent_role`に合致し、かつ`in-progress`や`needs-review`ラベルが付いていないタスクを候補としてフィルタリングします。
    *   **ソート:** 候補Issueを**Issue番号の昇順（作成順）**でソートします。

5.  **タスク割り当て処理:**
    *   ソートされた順に各候補Issueをチェックします。
    *   **ロック取得:** 割り当て試行中の競合を防ぐため、`RedisClient`を介してIssueごとの分散ロック (`issue_lock_{issue_id}`) の取得を試みます。
    *   **前提条件チェック:** ロック取得後、Issue本文に「成果物」セクションが定義されているかなどの前提条件をチェックします。
    *   ロック取得と前提条件チェックに成功した最初のIssueが、割り当てタスクとして決定されます。
6.  **タスク割り当てとレスポンス:**
    *   **GitHub操作:** `GitHubClient`を介して、タスク用のブランチを作成し、Issueに`in-progress`と`[agent_id]`ラベルを付与します。
    *   **プロンプト生成:** `GeminiExecutor`を呼び出し、IssueのURLやブランチ名などの情報から、エージェントが実行すべきプロンプトを生成します。
    *   **状態保存:** `RedisClient`に、エージェントが現在どのIssueに取り組んでいるか (`agent_current_task:{agent_id}`) を記録します。
    *   **レスポンス:** 割り当てられたタスク情報（Issue ID, URL, プロンプトなど）を含む`TaskResponse`を生成し、ワーカーエージェントに`200 OK`として返します。

7.  **タスクなし (ロングポーリング継続):** 初回チェックでタスクが見つからなかった場合、`request_task`は`asyncio.sleep`を挟みながら`_check_for_available_task(is_first_check=False)`の呼び出しを繰り返します。ループ中にタスクが見つかれば、その時点でステップ6に進みます。

8.  **タイムアウト:** ロングポーリングがタイムアウトした場合、APIサーバーは`204 No Content`をワーカーエージェントに返します。