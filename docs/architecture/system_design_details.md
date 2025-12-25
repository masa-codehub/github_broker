# System Design Details

**Note:** This file contains detailed system design information (sequence diagrams, robustness notes) that was previously in `system_context.md`. It is preserved here for reference.

## システム詳細シーケンス図 (Legacy)

```mermaid
sequenceDiagram
    participant Worker as ワーカーエージェント
    participant ApiServer as APIサーバー
    participant Redis
    participant PollingService as ポーリングサービス (Background)
    participant GitHub

    loop 定期的なポーリング
        PollingService->>+GitHub: GET /issues (オープンなIssueを全て取得, -label:"needs-review")
        GitHub-->>-PollingService: Issue List
        PollingService->>+Redis: SET open_issues (Issueリストをキャッシュ)
        Redis-->>-PollingService: OK
    end

    Worker->>+ApiServer: POST /request-task // ApiServerをアクティブ化 (+)
    ApiServer->>ApiServer: 1. 前タスクの完了処理 (ラベル更新)
    ApiServer->>GitHub: PATCH /issues/{prev_id}
    GitHub-->>ApiServer: OK

    ApiServer->>ApiServer: (ロングポーリング開始：内部でタスクを繰り返し検索...)
    ApiServer->>Redis: GET open_issues (キャッシュからIssueリストを取得)
    Redis-->>ApiServer: Issue List from Cache

    alt キャッシュから割り当て可能なタスクが見つかった場合
        ApiServer->>Redis: SETNX issue_lock_{issue_id} (個別Issueロック)
        Redis-->>ApiServer: OK
        ApiServer->>GitHub: PATCH /issues/{new_id} (ラベル更新)
        GitHub-->>ApiServer: OK
        ApiServer->>GitHub: POST /git/refs (ブランチ作成)
        GitHub-->>ApiServer: OK
        ApiServer-->>-Worker: 200 OK (新タスク情報) // ApiServerを非アクティブ化 (-)
    else キャッシュから割り当て可能なタスクが見つからずタイムアウトした場合
        ApiServer-->>Worker: 204 No Content // ここでもApiServerを非アクティブ化 (-)
    end
```

----

#### 8. 堅牢性のための設計

  * **GitHub APIの特性への対応:**
      * **ブランチが既に存在する場合 (`422 Reference already exists`) はエラーとせず、処理を続行する。**

----

#### 9. 技術スタック（推奨）
