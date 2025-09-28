# `github_broker` コードドキュメント

このドキュメントは、`github_broker` プロジェクトのコードベースにおける各ファイルの機能と役割を可視化することを目的としています。クリーンアーキテクチャの原則に基づき、各レイヤー（Domain, Application, Interface, Infrastructure）に分割して説明します。

## フォルダ構成

```
github_broker/
├── application/    # Application-specific business rules (Use Cases)
│   ├── __init__.py
│   ├── exceptions.py
│   └── task_service.py
├── domain/         # Enterprise-wide business rules
│   ├── __init__.py
│   └── task.py
├── infrastructure/ # Frameworks, Drivers (DB, Web, UI)
│   ├── agent/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── executors/
│   │   ├── __init__.py
│   │   └── gemini_executor.py
│   ├── __init__.py
│   ├── di_container.py
│   ├── gemini_client.py
│   ├── github_client.py
│   └── redis_client.py
└── interface/      # Adapters (Controllers, Presenters)
    ├── __init__.py
    ├── api.py
    └── models.py
```

## 各レイヤーの概要とファイル詳細

### 1. Domain Layer (ドメイン層)

エンタープライズ全体のビジネスルールを定義します。この層は他のどの層にも依存しません。

-   **`github_broker/domain/__init__.py`**
    -   **概要**: `task.py`で定義された`Task`クラスをエクスポートします。
    -   **主要なクラス/関数**: なし

-   **`github_broker/domain/task.py`**
    -   **概要**: GitHub Issueの情報を表現するデータクラスと、それに付随するビジネスロジックを定義します。
    -   **主要なクラス/関数**:
        -   `Task` (dataclass): Issue ID, タイトル, 本文, URL, ラベルを保持します。
        -   `is_assignable()`: Issueがアサイン可能かどうかをチェックします。（TODO: ロジック移動予定）
        -   `extract_branch_name()`: Issueの本文からブランチ名を抽出します。

### 2. Application Layer (アプリケーション層)

アプリケーション固有のビジネスルール（ユースケース）を定義します。ドメイン層に依存しますが、インターフェース層やインフラストラクチャ層には依存しません。

-   **`github_broker/application/__init__.py`**
    -   **概要**: 空のファイル。パッケージとして機能します。
    -   **主要なクラス/関数**: なし

-   **`github_broker/application/exceptions.py`**
    -   **概要**: アプリケーション固有のカスタム例外を定義します。
    -   **主要なクラス/関数**:
        -   `LockAcquisitionError`: タスクのロック取得に失敗した場合に発生する例外。

-   **`github_broker/application/task_service.py`**
    -   **概要**: GitHub Issueの管理、タスクのアサイン、ブランチの作成、そしてサーバーサイドでのプロンプト生成など、アプリケーションの主要なビジネスロジックを担うサービスです。インフラストラクチャ層のクライアント（Redis, GitHub, GeminiExecutor）をDIで受け取ります。`GeminiExecutor`を使用してプロンプトを生成し、そのプロンプトを基に最適なIssueを選択します。

### 3. Interface Layer (インターフェース層)

外部とのインターフェース（APIエンドポイント、データモデル）を定義します。アプリケーション層に依存しますが、インフラストラクチャ層には直接依存しません。

-   **`github_broker/interface/__init__.py`**
    -   **概要**: 空のファイル。パッケージとして機能します。
    -   **主要なクラス/関数**: なし

-   **`github_broker/interface/api.py`**
    -   **概要**: FastAPIアプリケーションを定義し、外部からのAPIリクエストを受け付けるエンドポイントを提供します。
    -   **主要なクラス/関数**:
        -   `app` (FastAPI): FastAPIアプリケーションインスタンス。
        -   `get_task_service()`: DIコンテナから`TaskService`を解決するための依存性注入関数。
        -   `lock_acquisition_exception_handler()`: `LockAcquisitionError`発生時の例外ハンドラ。
        -   `request_task_endpoint()`: `/request-task`エンドポイント。`TaskService`を利用してタスクをリクエストし、`TaskResponse`を返します。

-   **`github_broker/interface/models.py`**
    -   **概要**: APIのリクエストボディとレスポンスボディのデータ構造をPydanticモデルとして定義します。
    -   **主要なクラス/関数**:
        -   `AgentTaskRequest` (BaseModel): エージェントからのタスクリクエストのデータ構造（agent_id, capabilities）。
        -   `TaskResponse` (BaseModel): 割り当てられたタスク情報のレスポンスデータ構造（issue_id, issue_url, title, body, labels, branch_name）。

### 4. Infrastructure Layer (インフラストラクチャ層)

フレームワークやドライバ（DB、Web、UIなど）といった技術的な詳細を扱います。ドメイン層やアプリケーション層に依存されますが、これらの層はインフラストラクチャ層に依存しません。

-   **`github_broker/infrastructure/__init__.py`**
    -   **概要**: `agent.client`と`executors.gemini_executor`で定義されたクラスをエクスポートします。
    -   **主要なクラス/関数**: なし

-   **`github_broker/infrastructure/di_container.py`**
    -   **概要**: `punq`ライブラリを使用してDIコンテナをセットアップします。アプリケーション全体で使用される各種クライアント（Redis, GitHub, Gemini）やサービス（TaskService）の依存関係を解決し、シングルトンとして登録します。
    -   **主要なクラス/関数**:
        -   `container` (punq.Container): DIコンテナインスタンス。

-   **`github_broker/infrastructure/gemini_client.py`**
    -   **概要**: Google Gemini APIと連携するためのクライアントです。`GeminiExecutor`が生成したプロンプトをLLMに渡し、その結果に基づいて最適なIssueを選択する機能を提供します。
    -   **主要なクラス/関数**:
        -   `GeminiClient`:
            -   `__init__()`: Gemini APIキーを設定し、モデルをセットアップします。
            -   `select_best_issue_id(prompt: str) -> int | None`: Gemini APIを使用して、与えられたプロンプトに基づいて最適なIssue IDを選択します。

-   **`github_broker/infrastructure/github_client.py`**
    -   **概要**: PyGithubライブラリを使用してGitHub APIと連携するためのクライアントです。Issueの取得、ラベルの追加/削除、ブランチの作成など、GitHubリポジトリ操作に関する機能を提供します。
    -   **主要なクラス/関数**:
        -   `GitHubClient`:
            -   `__init__()`: GitHubトークンを設定し、クライアントを初期化します。
            -   `get_open_issues(repo_name: str)`: 進行中でないオープンなIssueを取得します。
            -   `find_issues_by_labels(repo_name: str, labels: list[str])`: 指定されたラベルを持つIssueを検索します。
            -   `add_label(repo_name: str, issue_id: int, label: str)`: Issueにラベルを追加します。
            -   `update_issue()`: Issueのラベルを更新します。
            -   `remove_label()`: Issueからラベルを削除します。
            -   `create_branch()`: ベースブランチから新しいブランチを作成します。

-   **`github_broker/infrastructure/redis_client.py`**
    -   **概要**: Redisとの連携機能を提供するクライアントです。主に分散ロックの取得と解放、値の取得と設定、キーの削除といった機能が含まれます。
    -   **主要なクラス/関数**:
        -   `RedisClient`:
            -   `__init__()`: Redisインスタンスを受け取り初期化します。
            -   `acquire_lock()`: ロックを取得します。
            -   `release_lock()`: ロックを解放します。
            -   `get_value()`: Redisから値を取得します。
            -   `set_value()`: Redisに値を設定します。
            -   `delete_key()`: Redisからキーを削除します。

-   **`github_broker/infrastructure/agent/client.py`**
    -   **概要**: GitHubタスクブローカーサーバーとHTTP経由で通信するためのクライアントです。**プロンプト生成ロジックには関与せず、サーバーから受け取ったタスクを実行するシンプルな役割を担います。**
    -   **主要なクラス/関数**:
        -   `AgentClient`:
            -   `__init__()`: エージェントID, 役割, サーバーホスト, ポートを設定し初期化します。
            -   `request_task()`: サーバーに新しいタスクをリクエストします。

-   **`github_broker/infrastructure/executors/gemini_executor.py`**
    -   **概要**: **サーバーサイドでのプロンプト生成ロジックを担う主要なコンポーネントです。** プロンプトテンプレートとタスク情報を基に、クライアントがLLMに渡す自然言語プロンプトを構築します。
    -   **主要なクラス/関数**:
        -   `GeminiExecutor`:
            -   `__init__()`: プロンプトテンプレートのパスなどを設定し初期化します。
            -   `build_prompt()`: タスク情報に基づいてプロンプトを構築します。
