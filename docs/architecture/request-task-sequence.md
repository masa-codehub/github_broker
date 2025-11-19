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

    TaskService->>+RedisClient: get_keys_by_pattern("issue:*")
    RedisClient-->>-TaskService: issue_keys
    TaskService->>+RedisClient: get_values(issue_keys)
    RedisClient-->>-TaskService: Cached Issues List

    Note over TaskService: 厳格な優先度バケット方式 (ADR-015)
    TaskService->>TaskService: 全Issueから最高優先度を決定 (例: P0)
    TaskService->>TaskService: 最高優先度ラベルを持つIssueのみ候補化

    Note over TaskService: 役割ラベル、in-progress状態でフィルタリング
    TaskService->>TaskService: 役割に合うタスクを候補化
    Note over TaskService: レビューIssueの場合、Redisのタイムスタンプを確認し、<br/>遅延時間(5分)経過後のみ候補に含める。

    alt 割り当て可能なタスク候補あり
        TaskService->>TaskService: 候補Issueを優先度ラベル順にソート
        
        loop 各候補Issue
            TaskService->>+RedisClient: acquire_lock(issue_lock_{issue_id})
            RedisClient-->>-TaskService: Lock Acquired or Not Acquired
            
            alt Lock Acquired
                TaskService->>+GitHubClient: create_branch(branch_name)
                GitHubClient-->>-TaskService: OK
                TaskService->>+GitHubClient: add_label(issue_id, ["in-progress", "{agent_id}"])
                GitHubClient-->>-TaskService: OK

                alt is Review Task? (ADR-016)
                    Note over TaskService: 'needs-review' ラベルで判断
                    TaskService->>+GitHubClient: get_pr_for_issue(issue_id)
                    GitHubClient-->>-TaskService: Pull Request Info (pr_url, pr_number)
                    TaskService->>+GitHubClient: get_pull_request_review_comments(pr_number)
                    GitHubClient-->>-TaskService: Review Comments
                    TaskService->>+GeminiExecutor: build_code_review_prompt(pr_url, review_comments)
                    GeminiExecutor-->>-TaskService: prompt_string
                else is Development Task
                    TaskService->>+GeminiExecutor: build_prompt(issue_url, branch_name)
                    GeminiExecutor-->>-TaskService: prompt_string
                end

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
-   **GeminiExecutor:** サーバーサイドでのプロンプト生成ロジックを担います。

### 3.2. 処理フロー

1.  **タスク要求:** ワーカーエージェントは、自身の`agent_id`を添えてAPIサーバーの`/request-task`エンドポイントにPOSTリクエストを送信します。

2.  **前タスクの完了処理:** `TaskService`は、まずエージェントに以前割り当てられていた`in-progress`状態のタスクがないか検索します。もし存在すれば、そのIssueのラベルを`needs-review`に更新し、`in-progress`と`[agent_id]`ラベルを削除します。

3.  **タスク候補の選定 (ADR-015準拠):**
    *   **キャッシュ一括取得:** `RedisClient`を介して、バックグラウンドで定期的にキャッシュされている全Issue (`issue:*`) を一括で取得します。
    *   **最高優先度の決定:** 取得した全Issueのラベル情報を基に、現在オープン状態のタスクの中で最も高い優先度レベル（例: `P0`）を特定します。
    *   **厳格な優先度フィルタリング:** 特定した最高優先度レベルのラベルを持つIssueのみを、タスク割り当ての候補とします。これ以外の優先度のIssueは、この段階で全て除外されます。
    *   **追加フィルタリング:**
        *   `in-progress`ラベルが付いていないタスクを候補とします。
        *   各Issueに付与された役割ラベル（例: `BACKENDCODER`）を解釈し、タスクを絞り込みます。
        *   **開発タスク:** `needs-review`ラベルが付いていないタスクを候補とします。
        *   **レビュータスク:** `needs-review`ラベルが付いているタスクは、Redisに保存された検出タイムスタンプを確認し、設定された遅延時間（`REVIEW_ASSIGNMENT_DELAY_MINUTES`）が経過した後でのみ候補に含めます。
        *   さらに、各Issueに付与された役割ラベル（例: `BACKENDCODER`）を解釈し、タスクを絞り込みます。
    *   **ソート:** フィルタリングされた候補Issueを、Issue番号順などの決定的な順序でソートします。

4.  **タスク割り当て処理:**
    *   ソートされた順に各候補Issueをチェックします。
    *   **ロック取得:** 割り当て試行中の競合を防ぐため、`RedisClient`を介してIssueごとの分散ロック (`issue_lock_{issue_id}`) の取得を試みます。
    *   **前提条件チェック:** ロック取得後、Issue本文に「成果物」セクションが定義されているかなどの前提条件をチェックします。
    *   ロック取得と前提条件チェックに成功した最初のIssueが、割り当てタスクとして決定されます。

5.  **タスク割り当てとレスポンス (ADR-016準拠):**
    *   **GitHub操作:** `GitHubClient`を介して、タスク用のブランチを作成し、Issueに`in-progress`と`[agent_id]`ラベルを付与します。
    *   **プロンプト生成 (分岐処理):**
        *   **レビュータスクの場合 (`needs-review`ラベルあり):**
            1.  `GitHubClient`を呼び出し、Issue番号に紐づく**Pull RequestのURLと番号**を取得します。
            2.  取得したPull Request番号を使い、`GitHubClient`を再度呼び出して**レビューコメントのリスト**を取得します。
            3.  `GeminiExecutor`の`build_code_review_prompt`メソッドを呼び出し、PRのURLとレビューコメントを基にレビュー修正用のプロンプトを生成します。
        *   **開発タスクの場合:**
            1.  `GeminiExecutor`の`build_prompt`メソッドを呼び出し、IssueのURLやブランチ名などの情報から開発用のプロンプトを生成します。
    *   **状態保存:** `RedisClient`に、エージェントが現在どのIssueに取り組んでいるか (`agent_current_task:{agent_id}`) を記録します。
    *   **レスポンス:** 割り当てられたタスク情報（Issue ID, URL, プロンプト, タスクタイプなど）を含む`TaskResponse`を生成し、ワーカーエージェントに`200 OK`として返します。

6.  **タスクなしの場合:** 割り当て可能なタスクが見つからなかった場合、APIサーバーは`204 No Content`をワーカーエージェントに返します。（注: ロングポーリングのロジックは簡略化のため、この図では省略されています。）
