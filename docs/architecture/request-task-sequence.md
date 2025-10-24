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
    Note over TaskService: レビューIssueの場合、Redisのタイムスタンプを確認し、\n遅延時間(5分)経過後のみ候補に含める。

    alt 割り当て可能なタスク候補あり
        TaskService->>TaskService: 最高優先度バケットで候補Issueをフィルタリング
        
        loop 各候補Issue
            TaskService->>+RedisClient: acquire_lock(issue_lock_{issue_id})
            RedisClient-->>-TaskService: Lock Acquired or Not Acquired
            
            alt Lock Acquired
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
                break loop
            else Lock Not Acquired
                Note over TaskService: ロック取得失敗、次の候補へ
                TaskService->>TaskService: 次の候補Issueへ
            end
        end

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
-   **RedisClient:** Redisとの通信を担当し、Issueのキャッシュ読み取りや分散ロック、遅延タスク管理を行います。
-   **GitHubClient:** GitHub APIとの通信を担当し、Issueの取得、ラベルの更新、ブランチの作成などを行います。

### 3.2. 処理フロー

1.  **タスク要求とロングポーリング:** ワーカーエージェントは、自身の`agent_id`を添えてAPIサーバーの`/request-task`エンドポイントにPOSTリクエストを送信します。サーバーはリクエストを受け取ると`TaskService`の`request_task`メソッドを呼び出します。このメソッドはロングポーリングで動作し、割り当て可能なタスクが見つからない場合は、指定されたタイムアウト時間までタスクの出現を待ち続けます。

2.  **初回タスクチェック:** `request_task`は、まず内部的に`_check_for_available_task(is_first_check=True)`を呼び出します。これが最初のチェックであることを示します。

3.  **前タスクの完了処理:** `is_first_check`が`True`の場合のみ、エージェントに以前割り当てられていた`in-progress`状態のタスクがないか検索します。もし存在すれば、そのIssueのラベルを`needs-review`に更新し、`in-progress`と`[agent_id]`ラベルを削除します。

4.  **タスク候補の選定:**
    *   **キャッシュ取得:** `RedisClient`を介して、バックグラウンドで定期的にキャッシュされているオープンなIssueのリスト (`open_issues`) を取得します。
    *   **候補フィルタリング:** Redisから取得したIssueリストから、`in-progress`ラベルが付いていないタスクを候補としてフィルタリングします。
        *   **開発タスク:** `needs-review`ラベルが付いていないタスクを候補とします。
        *   **レビュータスク:** `needs-review`ラベルが付いているタスクは、Redisに保存された検出タイムスタンプを確認し、設定された遅延時間（`REVIEW_ASSIGNMENT_DELAY_MINUTES`）が経過した後でのみ候補に含めます。
        *   さらに、各Issueに付与された役割ラベル（例: `BACKENDCODER`）を解釈し、タスクを絞り込みます。
    *   **優先度バケットによるフィルタリング:**
        *   まず、オープン状態のIssueの中から、最も高い優先度レベル（例: `P0`）を特定します。
        *   `TaskService`は、この最高優先度レベルのラベルを持つIssueのみを、タスク割り当ての候補とします。最高優先度以外のIssueは、たとえ割り当て可能な状態であっても、この段階で除外されます（厳格な優先度バケット方式）。
    *   **ソート:** フィルタリングされた候補Issueを、必要に応じて他の基準（例: 更新日時）でソートします。

5.  **タスク割り当て処理:**
    *   ソートされた順に各候補Issueをチェックします。
    *   **レビュータスクの遅延処理:** `needs-review`ラベルが付いているIssueの場合、`RedisClient`を介して遅延管理キー(`review_delay_{issue_id}`)の存在を確認します。
        *   キーが存在しない場合、現在の時刻を記録してキーを作成し、遅延計測を開始します。このIssueはスキップされ、次の候補Issueのチェックに移ります。
        *   キーが存在するものの、設定された遅延時間（デフォルト: 5分）が経過していない場合は、このIssueをスキップして次の候補に進みます。
        *   キーが存在し、設定された遅延時間（デフォルト: 5分）が経過している場合のみ、タスク割り当てに進みます。
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