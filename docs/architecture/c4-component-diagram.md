# C4モデル: コンポーネント図 (`github_broker`)

## 概要

これは、`github-broker`システムの内部アーキテクチャを、C4モデルのレベル2（コンポーネント図）で示したものです。
`github-broker`コンテナが、どのようなコンポーネントで構成されているかを示します。

## 図

```mermaid
C4Component
  title コンポーネント図 for GitHub Broker System

  Boundary(c1, "GitHub Broker System", "Python") {
    Component(api, "FastAPI Interface", "FastAPI", "エージェントからのタスク要求を受け付けるAPIエンドポイントを提供")
    Component(task_service, "Task Service", "Python", "タスクの選択、割り当て、プロンプト生成など、主要なビジネスロジックを担う")
    Component(di_container, "DI Container", "punq", "各コンポーネントの依存関係を解決・注入する")

    Boundary(c2, "Infrastructure Clients") {
      Component(github_client, "GitHub Client", "PyGithub", "GitHub APIとの通信を担う")
      Component(redis_client, "Redis Client", "redis-py", "Redisとの通信（キャッシュ、ロック）を担う")
      Component(gemini_client, "Gemini Client", "google.generativeai", "Google Gemini APIとの通信を担う")
    }
  }

  System_Ext(agent_system, "Agent System", "エージェントが動作する外部システム")
  System_Ext(github, "GitHub API", "")
  System_Ext(redis, "Redis", "インメモリデータストア")
  System_Ext(gemini, "Google Gemini API", "")

  Rel(agent_system, api, "タスクを要求する", "HTTPS/JSON")
  Rel(api, task_service, "ビジネスロジックの実行を依頼する")

  Rel(task_service, github_client, "IssueやPRの情報を取得・更新")
  Rel(task_service, redis_client, "Issueのキャッシュや分散ロックを操作")

  Rel(github_client, github, "Read/Write")
  Rel(redis_client, redis, "Read/Write")
  Rel(gemini_client, gemini, "Read/Write")

  UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="2")
```

## コンポーネント

### `FastAPI Interface`

-   **責務:** 外部からのHTTPリクエストを受け付けるインターフェース層。
-   **詳細:** `/request-task` などのエンドポイントを公開し、リクエストの検証を行った後、`Task Service`に処理を委譲します。

### `Task Service`

-   **責務:** アプリケーションのコアとなるビジネスロジック（ユースケース）を実行します。
-   **詳細:** タスクの選択（優先度判定、遅延処理）、ロック取得、プロンプト生成、状態更新など、タスク割り当てに関する一連の複雑なフローを管理します。

### `DI Container`

-   **責務:** `punq`ライブラリを使用し、各コンポーネントの依存関係を解決し、注入します。
-   **詳細:** アプリケーション起動時に、`GitHub Client`や`Redis Client`などのインスタンスを生成し、`Task Service`などに渡します。詳細は `di-container.md` を参照。

### `Infrastructure Clients`

-   **`GitHub Client`:** `PyGithub`ライブラリのラッパー。GitHub APIとの通信に責任を持ちます。
-   **`Redis Client`:** `redis-py`ライブラリのラッパー。Redisへのデータキャッシュや分散ロックの取得・解放に責任を持ちます。
-   **`Gemini Client`:** Google Gemini APIとの通信に責任を持ちます。
