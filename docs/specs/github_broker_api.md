# GitHub Broker API 仕様書

このドキュメントは、`github_broker` が提供する RESTful API の仕様を定義します。
APIは [OpenAPI Specification (OAS) v3](https://spec.openapis.org/oas/v3.0.0) に準拠する形で記述されています。

## 基本情報

- **ベースURL:** `/` (ローカル開発環境では `http://localhost:8000`)
- **コンテンツタイプ:** リクエストおよびレスポンスは、特に指定がない限り `application/json` を使用します。

## エンドポイント

### 1. ヘルスチェック

アプリケーションの稼働状態を確認します。

- **パス:** `/health`
- **メソッド:** `GET`

#### レスポンス

- **200 OK**: 正常に稼働中。

  ```json
  {
    "status": "ok"
  }
  ```

### 2. タスクリクエスト

**⚠️ 現在のステータス: メンテナンス中 (Stubbed)**
現在、このエンドポイントはリファクタリング中のためスタブ化されており、常に `204 No Content` を返します。
以下の仕様は、リファクタリング完了後の動作目標を表しています。

エージェントが実行可能なタスクをリクエストします。

- **パス:** `/request-task`
- **メソッド:** `POST`

#### リクエストボディ

`AgentTaskRequest` オブジェクト。

```json
{
  "agent_id": "string"
}
```

| フィールド | 型     | 必須 | 説明 |
| :--- | :--- | :--- | :--- |
| `agent_id` | `string` | Yes  | リクエストを行うエージェントの一意識別子。 |

#### レスポンス

- **200 OK**: タスクが割り当てられた場合。

  **レスポンスボディ (`TaskResponse`):**

  ```json
  {
    "issue_id": 123,
    "issue_url": "https://github.com/owner/repo/issues/123",
    "title": "Issue Title",
    "body": "Issue Body Content...",
    "labels": ["label1", "label2"],
    "branch_name": "feature/issue-123",
    "prompt": "Generated prompt for the agent...",
    "required_role": "BACKEND_CODER",
    "task_type": "development",
    "gemini_response": null
  }
  ```

  | フィールド | 型 | 説明 |
  | :--- | :--- | :--- |
  | `issue_id` | `integer` | GitHub Issue番号。 |
  | `issue_url` | `string` | IssueへのURL。 |
  | `title` | `string` | Issueのタイトル。 |
  | `body` | `string` | Issueの本文。 |
  | `labels` | `array[string]` | Issueに付与されているラベルのリスト。 |
  | `branch_name` | `string` | 作業用ブランチ名。 |
  | `prompt` | `string` | エージェントへの指示プロンプト。 |
  | `required_role` | `string` | このタスクを実行するために必要な役割。 |
  | `task_type` | `string` | タスクの種類 (`development`, `review`, `fix`)。 |
  | `gemini_response` | `string` | (Optional) Geminiからの応答が含まれる場合。 |

- **204 No Content**: 現在割り当て可能なタスクがない場合。

- **422 Unprocessable Entity**: リクエストボディのバリデーションエラー。

### 3. 修正タスク作成

プルリクエストのレビューコメントに基づき、修正タスクを作成します。

- **パス:** `/tasks/fix`
- **メソッド:** `POST`

#### リクエストボディ

**(注: 現在の実装ではスタブ状態であり、スキーマは完全に定義されていません)**

#### レスポンス

- **202 Accepted**: リクエストが受け付けられた場合。

  ```json
  {
    "message": "Fix task creation has been accepted (stubbed)."
  }
  ```
