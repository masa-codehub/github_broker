# 依存性注入(DI)コンテナ 設計書

## 1. 概要

このドキュメントは、`github_broker`プロジェクトにおける依存性注入（DI）の設計と実装について説明します。
本プロジェクトでは、コンポーネント間の依存関係を疎結合に保ち、テスト容易性を向上させる目的で、軽量なDIコンテナライブラリ `punq` を採用しています。

依存関係の定義は、すべて `/github_broker/infrastructure/di_container.py` に一元管理されています。

## 2. `punq` の役割

`punq` は、アプリケーションの起動時に各コンポーネント（サービスやクライアント）のインスタンスを生成し、必要な場所に注入（inject）する役割を担います。

- **一元管理:** コンポーネントの生成方法とライフサイクル（例: シングルトン）を1つのファイルで管理できます。
- **疎結合:** コンポーネントは、自身が依存する他のコンポーネントの具体的な生成方法を知る必要がなくなります。インターフェース（抽象）に依存し、具体的な実装はDIコンテナが提供します。
- **テスト容易性:** 単体テストの際に、本物のコンポーネントの代わりにモックやスタブを容易に差し替えることができます。

## 3. 登録済みサービス

現在、以下のコンポーネントがシングルトン（アプリケーション全体で唯一のインスタンス）として登録されています。

- `RedisClient`: Redisサーバーとの通信を担当します。
- `GitHubClient`: GitHub APIとの通信を担当します。
- `TaskService`: タスクの取得や割り当てといったコアなビジネスロジックを担当します。
- `GeminiExecutor`: Gemini APIとの通信を担当し、プロンプトの実行を行います。

```python
# /github_broker/infrastructure/di_container.py (抜粋)

# DIコンテナの初期化
container = punq.Container()

# RedisClientの登録
# ...
container.register(RedisClient, instance=RedisClient(redis_instance))

# GitHubClientの登録
container.register(GitHubClient, scope=punq.Scope.singleton)

# GeminiExecutorの登録
container.register(GeminiExecutor, scope=punq.Scope.singleton)

# TaskServiceの登録
container.register(
    TaskService,
    instance=TaskService(
        redis_client=container.resolve(RedisClient),
        github_client=container.resolve(GitHubClient),
        gemini_executor=container.resolve(GeminiExecutor),
    ),
)
```

## 4. 新しいサービスの追加・変更方法

新しいサービスやクライアント（例: `NewApiClient`）を追加する場合、以下の手順で `di_container.py` を編集します。

### 手順

1.  **インポート:** 新しいクラスをインポートします。
2.  **登録:** `container.register()` を使って、新しいクラスをコンテナに登録します。多くの場合、ライフサイクルは `scope=punq.Scope.singleton` となります。
3.  **依存の注入:** 新しいクラスが他のコンポーネントに依存している場合は、`container.resolve()` を使って依存性を解決し、コンストラクタに渡します。

### 例: `GeminiExecutor` を追加する場合

```python
# 1. GeminiExecutorをインポート
from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor

# ... (既存のコード)

# 2. GeminiExecutorをシングルトンとして登録
container.register(GeminiExecutor, scope=punq.Scope.singleton)

# TaskServiceがGeminiExecutorに依存するようになった場合
container.register(
    TaskService,
    instance=TaskService(
        redis_client=container.resolve(RedisClient),
        github_client=container.resolve(GitHubClient),
        # 3. 新しい依存性を解決して注入
        gemini_executor=container.resolve(GeminiExecutor),
    ),
    scope=punq.Scope.singleton,
)
```

このように、依存関係の変更はすべてこのファイル内で完結するため、アプリケーションの他の部分への影響を最小限に抑えることができます。
