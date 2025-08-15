# GitHubタスクブローカー

このシステムは、複数の自律型ワーカーエージェントに対し、GitHubのIssueを知的かつ排他的に割り当てるための中央集権型サーバーです。エージェント間の競合を防ぎ、開発ワークフローの自動化と効率化を実現します。

このシステムは、クリーンアーキテクチャとテスト駆動開発の原則に基づいて構築されています。

## 前提条件

*   Docker
*   Docker Compose

## 設定

1.  **環境ファイルの作成**:
    サンプルファイル `.build/context/.env.sample` をコピーして `.env` ファイルを作成します。このファイルにローカル環境変数を設定します。
    ```bash
    cp .build/context/.env.sample .env
    ```

2.  **環境変数の設定**:
    `.env` ファイルを開き、以下の変数を設定してください。

    *   `GH_TOKEN`: GitHub APIと連携するための、`repo`スコープを持つ個人のGitHubアクセストークン。
    *   `GITHUB_REPOSITORY`: ブローカーが管理するリポジトリ名 (例: `your-username/your-repo`)。

    `.env` ファイルの例:
    ```
    GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    GITHUB_REPOSITORY=your_github_account/your_github_repository
    ```

## 実行方法

設定が完了したら、以下のコマンドでAPIサーバーとRedisを含むシステム全体をDocker Composeを使って起動します。

```bash
docker-compose -f /docker-compose.yaml up --build
```

APIサーバーは `http://localhost:8000` で利用可能になります。

## APIの使用方法

`POST`リクエストを`/api/v1/request-task`エンドポイントに送信することで、新しいタスクを要求できます。

**`curl`を使用した例:**

```bash
curl -X POST "http://localhost:8000/api/v1/request-task" \
-H "Content-Type: application/json" \
-d '{
  "agent_id": "my-test-agent-1",
  "capabilities": ["python", "bugfix", "fastapi"]
}'
```

### レスポンス

*   **200 OK**: 適切なタスクが見つかり、割り当てられました。レスポンスボディにはIssueの詳細と新しいブランチ名が含まれます。
    ```json
    {
      "issue_id": 123,
      "issue_url": "https://github.com/owner/repo/issues/123",
      "title": "ログインボタンの色を修正",
      "body": "ログインボタンは赤ではなく青であるべきです...",
      "labels": ["bug", "ui"],
      "branch_name": "feature/issue-123"
    }
    ```
*   **204 No Content**: 現時点で、エージェントの能力に合った適切なタスクが見つかりませんでした。
*   **503 Service Unavailable**: サーバーが他のエージェントのリクエストを処理中でビジー状態です。後でもう一度お試しください。