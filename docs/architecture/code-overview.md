# コードの概要 (Code Overview)

このドキュメントは、本プロジェクトのコードベースにおける各コンポーネントの機能と役割、および詳細な構造を説明します。

## コンポーネントの責務と境界 (Component Responsibilities and Boundaries)

本システムは、開発ライフサイクルの異なるフェーズを担う2つの独立したコンポーネントで構成されています。

### 1. `github_broker` (Agent Runtime & Orchestrator)
**「タスクを実行し、完了させる」ための常駐サービス**

-   **位置づけ**: システムの中核エンジン（バックエンドサービス）。
-   **実行モデル**: 常時稼働し、GitHub APIをポーリング、またはWebhookを受け取って動作します。
-   **主な責務**:
    -   **タスクオーケストレーション**: GitHub Issueをタスク単位として認識し、Redisを用いた優先度管理・排他制御を行います。
    -   **エージェントインターフェース**: AIエージェント（Worker）に対して、標準化されたタスク実行指示（プロンプト）を提供し、成果を受け取ります。
    -   **自律的な進行**: 人間の介入を待たず、Issueの状態（ラベルなど）に基づいて自律的に開発プロセスを進めます。
-   **主な機能**:
    -   GitHub APIを通じたIssueの監視と取得
    -   Redisを使用したタスクの優先度管理と分散ロック
    -   Gemini APIを使用したAIエージェントによるタスク実行（コード生成、レビュー修正など）
    -   APIエンドポイントの提供（エージェントからのリクエスト受付）

### 2. `issue_creator_kit` (Development Scaffolding & CI Tool)
**「タスクを定義し、品質を担保する」ためのCLIツールキット**

-   **位置づけ**: 開発者やCI/CDパイプラインが利用するユーティリティ（コマンドラインツール）。
-   **実行モデル**: ユーザー操作やCIイベント（Push, PR作成）をトリガーとして、ワンショットで実行されます。
-   **主な責務**:
    -   **タスク生成 (Scaffolding)**: `_in_box` 内の定義ファイルやテンプレートから、正規化されたGitHub Issueを自動生成します。これが `github_broker` の入力となります。
    -   **品質ガードレール**: ドキュメント（ADR, Design Doc）の構造や必須項目を検証し、ルール違反を早期に検出します。
    -   **ステートレス**: 実行のたびに完結し、永続的な状態管理は行いません。
-   **主な機能**:
    -   **Issue作成**: `_in_box` ディレクトリ内のMarkdownファイルを解析し、GitHub Issueを自動作成します。作成後はファイルを `_done_box` 等へ移動させます。
    -   **ドキュメント検証**: ADRやデザインドキュメントなどのMarkdownファイルが、所定のフォーマットや必須項目（Frontmatterなど）を満たしているかを検証します。

### 役割分担のまとめ

| 特徴 | github_broker | issue_creator_kit |
| :--- | :--- | :--- |
| **主な役割** | **Issueの消化** (解決・クローズ) | **Issueの供給** (作成・定義) & 検証 |
| **実行形態** | 常駐サービス (Server) | CLIツール (Client/Script) |
| **トリガー** | ポーリング / 時間駆動 | 手動 / Gitイベント (CI) |
| **状態管理** | Redisによるステートフル管理 | ステートレス |
| **ユーザー** | AIエージェント | 開発者, CIランナー |

---

## `github_broker` コードドキュメント

このセクションでは、`github_broker` ディレクトリ内のコード構成について説明します。クリーンアーキテクチャの原則に基づき、各レイヤー（Domain, Application, Interface, Infrastructure）に分割されています。

### フォルダ構成

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

### 各レイヤーの概要とファイル詳細

#### 1. Domain Layer (ドメイン層)

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

#### 2. Application Layer (アプリケーション層)

アプリケーション固有のビジネスルール（ユースケース）を定義します。ドメイン層に依存しますが、インターフェース層やインフラストラクチャ層には依存しません。

-   **`github_broker/application/__init__.py`**
    -   **概要**: 空のファイル。パッケージとして機能します。
    -   **主要なクラス/関数**: なし

-   **`github_broker/application/exceptions.py`**
    -   **概要**: アプリケーション固有のカスタム例外を定義します。
    -   **主要なクラス/関数**:
        -   `LockAcquisitionError`: タスクのロック取得に失敗した場合に発生する例外。

-   **`github_broker/application/task_service.py`**
    -   **概要**: アプリケーションの主要なビジネスロジックを担うサービスです。インフラストラクチャ層のクライアント（`GitHubClient`, `RedisClient`, `GeminiExecutor`）と設定（`Settings`）をDIで受け取ります。主な責務は以下の通りです。
        1.  **タスクのポーリングとキャッシュ:** 定期的にGitHubからIssueを取得し、Redisにキャッシュします。
        2.  **厳格な優先度に基づくタスク選択 (ADR-015):** Redisにキャッシュされた全Issueから最も高い優先度を特定し、その優先度のタスクのみを割り当て候補とします。
        3.  **タスク種別に応じたプロンプト生成 (ADR-016):**
            -   **開発タスク:** `GeminiExecutor`を呼び出し、開発用のプロンプトを生成します。
            -   **レビュー修正タスク:** `GitHubClient`でPR情報とレビューコメントを取得し、`GeminiExecutor`でレビュー修正専用のプロンプトを生成します。
        4.  **タスクの割り当てと状態管理:** 選択したタスクをロックし、エージェントに割り当て、その状態をRedisとGitHub上で更新します。

#### 3. Interface Layer (インターフェース層)

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

#### 4. Infrastructure Layer (インフラストラクチャ層)

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
            -   `get_open_issues()`: 進行中でないオープンなIssueを取得します。
            -   `get_review_issues()`: `needs-review`ラベルのついたIssueを取得します。
            -   `get_pr_for_issue(issue_number: int)`: Issue番号に紐づくPull Requestを取得します。
            -   `get_pull_request_review_comments(pull_number: int)`: Pull Request番号に紐づくレビューコメントを取得します。
            -   `find_issues_by_labels(labels: list[str])`: 指定されたラベルを持つIssueを検索します。
            -   `add_label(issue_id: int, label: str)`: Issueにラベルを追加します。
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
            -   `build_prompt()`: 開発タスクの情報に基づいてプロンプトを構築します。
            -   `build_code_review_prompt()`: レビュー修正タスクの情報（PRのURL、レビューコメント）に基づいてプロンプトを構築します。

---

## `issue_creator_kit` コードドキュメント

このセクションでは、`issue_creator_kit` ディレクトリ内のコード構成について説明します。こちらもクリーンアーキテクチャの影響を受けた構成となっています。

### フォルダ構成

```
issue_creator_kit/
├── application/    # Application-specific business rules (Use Cases)
│   ├── __init__.py
│   ├── issue_service.py      # Issue作成ロジック
│   ├── validation_service.py # ドキュメント検証ロジック
│   └── utils.py
├── domain/         # Enterprise-wide business rules
│   ├── __init__.py
│   ├── issue.py     # Issueデータモデル
│   └── document.py  # ドキュメント定義
├── infrastructure/ # Frameworks, Drivers
│   ├── __init__.py
│   ├── github_service.py      # GitHub API操作
│   └── file_system_service.py # ファイル操作
└── interface/      # Adapters (CLI)
    ├── __init__.py
    ├── cli.py            # Issue作成CLIのエントリーポイント
    └── validation_cli.py # バリデーションCLIのエントリーポイント
```

### 各レイヤーの概要とファイル詳細

#### 1. Domain Layer (ドメイン層)

ビジネスルールやデータ構造を定義します。

-   **`issue_creator_kit/domain/issue.py`**

    -   **概要**: GitHub Issueのデータを表現するデータクラスです。

    -   **主要なクラス**:

        -   `IssueData`: タイトル、本文、ラベル、アサイン情報を保 持します。

-   **`issue_creator_kit/domain/document.py`**

    -   **概要**: ドキュメントの種類や検証ルール（必須ヘッダーなど）を定義します。

    -   **主要なクラス/定数**:

        -   `DocumentType`: ドキュメントの種類（ADR, DESIGN_DOCな ど）を定義するEnum。

        -   `REQUIRED_HEADERS`: 各ドキュメントタイプに必要なヘッダー定義。

-   **`issue_creator_kit/domain/in_box_file_filter.py`**

    -   **概要**: `_in_box` ディレクトリ内のファイルをフィルタリングする機能を提供します。

    -   **主要なクラス/関数**:

        -   `filter_in_box_files(file_list: list[str]) -> list[str]`: ファイルリストから `_in_box/` で始まるパスのみを抽出して返します。

#### 2. Application Layer (アプリケーション層)

具体的なユースケースを実装します。

-   **`issue_creator_kit/application/exceptions.py`**

    -   **概要**: アプリケーション固有のカスタム例外を定義します。

    -   **主要なクラス**:

        -   `FrontmatterError`: フロントマターの検証中にエラーが発生した場合に送出されるカスタム例外。

-   **`issue_creator_kit/application/issue_service.py`**

    -   **概要**: `_in_box` 内のファイルからIssueを作成し、ファイ ルを移動させる一連のフローを制御します。

    -   **主要なクラス**:

        -   `IssueCreationService`:

            -   `create_issues_from_inbox(pull_number)`: 指定され たPRに関連するInboxファイルを処理し、Issueを作成します。成功・失敗に応じてファイルを移動します。

-   **`issue_creator_kit/application/validation_service.py`**

    -   **概要**: ドキュメントのフォーマット検証ロジックを提供します。

    -   **主要なクラス**:

        -   `ValidationService`:

            -   `validate_frontmatter(file_path)`: Markdownファイ ルのFrontmatter（メタデータ）を検証します。

            -   `validate_sections(content, doc_type)`: 必須セクションが含まれているか検証します。

-   **`issue_creator_kit/application/utils.py`**

    -   **概要**: ファイルパス生成などのユーティリティ関数を提供し ます。

    -   **主要なクラス/関数**:

        -   `get_unique_path(base_path: str, file_name: str) -> str`: ファイル名にタイムスタンプを付与して一意のファイルパスを生成 します。

#### 3. Interface Layer (インターフェース層)

CLIツールとしてのエントリーポイントを提供します。

-   **`issue_creator_kit/interface/cli.py`**

    -   **概要**: Issue作成ツールのエントリーポイントです。環境変 数や引数から設定を読み込み、`IssueCreationService`を実行します。

-   **`issue_creator_kit/interface/validation_cli.py`**

    -   **概要**: ドキュメント検証ツールのエントリーポイントです。指定されたディレクトリ内のファイルをスキャンし、`ValidationService`を使って検証を実行します。

#### 4. Infrastructure Layer (インフラストラクチャ層)

外部システム（GitHub API、ファイルシステム）との連携を扱います。

-   **`issue_creator_kit/infrastructure/github_service.py`**
    -   **概要**: `PyGithub` を使用してGitHub APIを操作します。
    -   **主要なクラス**:
        -   `GithubService`: Issueの作成、リポジトリ内のファイル取得などを行います。

-   **`issue_creator_kit/infrastructure/file_system_service.py`**
    -   **概要**: ローカルファイルシステムの操作（ファイルの探索、読み込みなど）を行います。
    -   **主要な関数**:
        -   `find_target_files(base_path: str) -> list[str]`: ADR-012で定義された対象ファイルを探索し、絶対パスのリストを返します。
        -   `read_file_content(file_path: str) -> str`: 指定されたファイルの内容を読み込んで返します。
