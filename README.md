# GitHub Task Broker

## 解決したい課題

複数の自律型AIエージェント（AI開発者）が、同じGitHubリポジトリ上で同時に作業すると、「どのタスク（Issue）を誰がやるのか」が分からなくなり、同じ作業を始めてしまうなどの**コンフリクト（競合）**が発生します。

このシステムは、中央集権的な司令塔として各エージェントからのタスク要求を調整し、知的かつ排他的にタスクを割り当てることで、この問題を解決します。

---

このシステムは、複数の自律型ワーカーエージェントに対し、GitHubのIssueを知的かつ排他的に割り当てるための中央集権型サーバーです。エージェント間の競合を防ぎ、開発ワークフローの自動化と効率化を実現します。

## 設計思想

このシステムは、クリーンアーキテクチャとテスト駆動開発(TDD)の原則に基づいて構築されています。

### クリーンアーキテクチャ

ソフトウェアを関心事によってレイヤーに分割することで、ビジネスロジックをフレームワークや外部サービスから独立させ、保守性、適応性、テスト容易性の高い構造を目指します。

-   `domain`: プロジェクト全体で共通のビジネスルール。最も安定した層。
-   `application`: ユースケース層。アプリケーション固有のビジネスロジックを実装。
-   `interface`: 外部との境界。API定義(FastAPI)やデータモデル(Pydantic)など。
-   `infrastructure`: 外部サービスとの連携。GitHub、Redis、Gemini APIクライアントなど。

## 1. 設定

アプリケーションの動作には、環境変数の設定が必要です。

### クイックスタート: `.env` ファイルの作成

すぐに試すには、サンプルファイルをコピーして`.env`ファイルを作成します。

```bash
cp .build/context/.env.sample .env
```

各変数の詳細な説明や設定値については、[運用・デプロイ要件定義書](./docs/architecture/operational-requirements.md#8-環境変数) を参照してください。

## 2. 実行方法

### 2.1. Dockerでの実行 (推奨)

設定が完了したら、以下のコマンドでAPIサーバーとRedisを含むシステム全体をDocker Composeを使って起動します。

```bash
docker-compose -f .build/context/docker-compose.yml up --build
```

APIサーバーは `http://localhost:8080` で利用可能になります。

### 2.2. ローカルでの実行 (開発用)

1.  **仮想環境の作成と有効化:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  **依存関係のインストール:**
    ```bash
    pip install -e .[test,dev]
    ```

3.  **サーバーの起動:**
    `.env` ファイルが読み込まれるようにして、uvicornでサーバーを起動します。
    ```bash
    uvicorn github_broker.interface.api:app --reload --port 8080
    ```

## 3. APIの使用方法

APIサーバーが起動したら、`POST`リクエストを`/api/v1/request-task`エンドポイントに送信することで、新しいタスクを要求できます。

### クイックスタート: `curl` でタスクをリクエストする

```bash
curl -X POST "http://localhost:8080/api/v1/request-task" \
-H "Content-Type: application/json" \
-d '{ "agent_id": "my-test-agent-1", "agent_role": "CODER" }'
```

各エンドポイントの詳細な仕様や他のリクエスト例については、[システム設計書](./docs/architecture/index.md#4-api仕様) を参照してください。


## 4. カンバンシステム (タスク状態管理)

本システムは、GitHubのラベルを利用してタスクの進行状況を管理します。

-   `in-progress`と`[agent_id]`: あるエージェントにタスクが割り当てられると、これら2つの状態ラベルが自動的にIssueに付与されます。これにより、特定のタスクがどのエージェントによって処理中であるかが一意に識別され、他のエージェントへの重複割り当てを防ぎます。
-   `needs-review`: エージェントが次のタスクをリクエストすると、前回割り当てられていたIssueから`in-progress`と`[agent_id]`のラベルが削除され、代わりにこのラベルが付与されます。これにより、人間によるレビュー待ちの状態であることを示します。