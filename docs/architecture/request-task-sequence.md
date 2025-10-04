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
        TaskService->>+RedisClient: set_value(needs_review_timestamp:{prev_issue_id}, current_timestamp)
        GitHubClient-->>-TaskService: OK
        RedisClient-->>-TaskService: OK
    end

    TaskService->>TaskService: 1. 役割に合うタスクを候補化 (フィルタリング)
    Note over TaskService: 優先度、needs-reviewラベル、待機時間を考慮

    alt 割り当て可能なタスク候補あり
        loop タスク候補の選定とロック取得
            TaskService->>TaskService: 候補Issueを優先度順にソート
            Note over TaskService: 優先度: needs-review (待機時間経過) > 通常タスク
            Note over TaskService: 各カテゴリ内で作成日時の古い順

            TaskService->>+RedisClient: acquire_lock(issue_lock_{selected_issue_id}, "locked", timeout=600)
            RedisClient-->>-TaskService: Lock Acquired / Failed

            alt ロック取得成功 & 前提条件(成果物セクション)満たす
                TaskService->>+GitHubClient: create_branch(branch_name, base_branch)
                GitHubClient-->>-TaskService: OK

                TaskService->>+GitHubClient: update_issue(selected_issue_id, add_labels=["in-progress", "{agent_id}"], remove_labels=["needs-review"])
                GitHubClient-->>-TaskService: OK
                TaskService->>+RedisClient: delete_value(needs_review_timestamp:{selected_issue_id})
                RedisClient-->>-TaskService: OK

                TaskService->>+RedisClient: set_value(agent_current_task:{agent_id}, selected_issue_id)
                RedisClient-->>-TaskService: OK

                TaskService-->>-ApiServer: TaskResponse (issue_id, url, title, body, labels, branch_name, prompt)
                ApiServer-->>-Worker: 200 OK (TaskResponse)
                break
            else ロック取得失敗 または 前提条件満たさない
                TaskService->>TaskService: 次の候補Issueをチェック / リトライ
            end
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
4.  **前タスクの完了処理:** エージェントに以前割り当てられていた`in-progress`状態のタスク(`prev_issue_id`)がないか確認します。もし存在すれば、そのIssueのラベルを`needs-review`に更新し、`in-progress`と`[agent_id]`ラベルを削除します。**この際、`needs-review`ラベルが付与された時刻を`RedisClient`に`needs_review_timestamp:{prev_issue_id}`として記録します。これは、後続のタスク選定ロジックで「レビューコメントを待つための時間」を判断するために使用されます。**
5.  **タスク候補の選定:**
    *   **候補のフィルタリング:** Redisから取得したIssueリストから、エージェントの`agent_role`に合致するタスクをフィルタリングします。
    *   **優先度付けと最適Issue選択:** フィルタリングされた候補Issueは、以下の優先順位に基づいてソートされ、最適なIssueが選択されます。
        1.  **`needs-review`かつレビューコメント待機時間経過済みのタスク:** `needs_review_timestamp`に記録された時刻から一定時間（例: 24時間）が経過した`needs-review`ラベル付きのタスクが最優先されます。これにより、レビュー待ちのタスクが放置されることなく、適切なタイミングで再処理の対象となります。
        2.  **通常のオープンタスク:** 上記以外の、`in-progress`や`needs-review`ラベルが付いていない通常のオープンタスク。
        各カテゴリ内では、Issueの作成日時が古いものから優先的に選択されます。
    *   **ロック取得:** 選択されたIssue (`selected_issue_id`) に対して、`RedisClient`を使用して分散ロックの取得を試みます。これにより、複数のエージェントが同時に同じIssueを処理することを防ぎます。
    *   **前提条件チェック:** ロック取得に成功した場合、Issueの本文に「成果物」セクションが正しく定義されているかなどの前提条件をチェックします。
6.  **タスク割り当てとレスポンス:**
    *   **ブランチ作成:** 新しいタスクとして選択されたIssueに対応するブランチを`GitHubClient`を介して作成します。
    *   **タスク割り当て:** 新しいタスクのIssueに`in-progress`と`[agent_id]`ラベルを付与し、もし`needs-review`ラベルが付いていた場合はそれを削除します。**また、`needs_review_timestamp:{selected_issue_id}`に記録された値も削除します。**
    *   **現在タスクの記録:** `RedisClient`に、エージェントが現在どのIssueに取り組んでいるか (`agent_current_task:{agent_id}`) を記録します。
    *   **レスポンス:** 割り当てられたタスク情報（Issue ID, URL, タイトル, 本文, ラベル, ブランチ名, プロンプト）を`TaskResponse`としてワーカーエージェントに返します。
7.  **タスクなし:** 割り当て可能なタスクが見つからなかった場合、APIサーバーは`204 No Content`を返します。