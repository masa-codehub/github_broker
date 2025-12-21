# 依存性注入(DI)コンテナ 設計書

## 1. 概要

このドキュメントは、`github_broker`プロジェクトにおける依存性注入（DI）の設計と実装について説明します。
本プロジェクトでは、コンポーネント間の依存関係を疎結合に保ち、テスト容易性を向上させる目的で、軽量なDIコンテナライブラリ `punq` を採用しています (ADR-004)。

依存関係の定義は、すべて `/github_broker/infrastructure/di_container.py` に一元管理されています。

## 2. 設計思想と登録方針

### 依存関係の一元管理

`di_container.py` の `create_container()` 関数内で、アプリケーションが必要とするすべての依存性をコンテナに登録します。

これにより、コンポーネントが自身の依存関係を直接生成（インスタンス化）するのではなく、コンテナから注入される形となり、モックへの差し替えが容易になります。

### ライフサイクル

- **`scope="singleton"`**: アプリケーション全体で単一のインスタンスを共有するサービス（例: `Settings`, `GitHubClient`, `RedisClient`）に対して使用します。
- **`transient` (指定なし)**: 呼び出しごとに新しいインスタンスが必要なサービスに対して使用します。

原則として、ステートレスなクライアントは `singleton`、特定のコンテキストに依存するサービスは必要に応じて `transient` とすることを推奨します。

## 3. 登録済みサービスと実装例

以下は、`di_container.py` における主要なサービスの登録例です。

```python
# /github_broker/infrastructure/di_container.py (抜粋)

import punq
import redis
from github_broker.application.task_service import TaskService
from github_broker.infrastructure.config import Settings, get_settings
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient

def create_container(settings: Settings | None = None) -> punq.Container:
    s = settings or get_settings()

    # 各種クライアントのインスタンス化
    github_client = GitHubClient(
        github_repository=s.github_agent_repository,
        github_token=s.github_personal_access_token,
    )
    redis_instance = redis.from_url(s.redis_url, decode_responses=True)
    redis_client = RedisClient(redis=redis_instance, ...)

    # コンテナの初期化と登録
    container = punq.Container()
    container.register(Settings, instance=s)
    container.register(GitHubClient, instance=github_client)
    container.register(RedisClient, instance=redis_client)
    
    # TaskServiceはファクトリを用いて登録
    container.register(
        TaskService,
        factory=lambda: TaskService(
            github_client=container.resolve(GitHubClient),
            redis_client=container.resolve(RedisClient),
            agent_configs=container.resolve(AgentConfigList),
        ),
    )
    return container
```

## 4. 開発ガイドライン：新しいサービスの追加方法

新しいサービス（例: `NewAnalyticsService`）を追加し、それを `TaskService` に注入する場合、以下の手順に従ってください。

1.  **サービスの登録:**
    `github_broker/infrastructure/di_container.py` の `create_container()` 関数内で、`NewAnalyticsService` の登録処理を追記します。

    ```python
    # github_broker/infrastructure/di_container.py

    def create_container(settings: Settings | None = None) -> punq.Container:
        ...
        # サービスをコンテナに登録
        container.register(NewAnalyticsService, scope=punq.Scope.singleton)
        ...
    ```

2.  **依存性の注入:**
    `TaskService` のコンストラクタで、`NewAnalyticsService` を引数として受け取るように修正し、`create_container` 内の `TaskService` 登録時のファクトリ関数（lambda）を更新します。

    ```python
    # github_broker/application/task_service.py
    class TaskService:
        def __init__(self, ..., new_service: NewAnalyticsService):
            self._new_service = new_service

    # github_broker/infrastructure/di_container.py
    container.register(
        TaskService,
        factory=lambda: TaskService(
            ...,
            new_service=container.resolve(NewAnalyticsService),
        ),
    )
    ```

このように、依存関係の変更は `di_container.py` 内で完結するため、アプリケーションの他の部分への影響を最小限に抑えることができます。
