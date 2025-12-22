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

本プロジェクトでは、以下の登録パターンを主に使用しています。

- **`instance=` (事前生成インスタンス)**: `Settings` や各種クライアントなど、初期化時に設定値が必要なオブジェクトは、コンテナ登録前にインスタンス化し、`instance` パラメータで登録します。これにより、実質的なシングルトンとして振る舞います。
- **`factory=` (ファクトリ関数)**: 依存関係の解決が必要なサービス（例: `TaskService`）は、`factory` パラメータにラムダ関数などを渡して登録します。解決時にコンテナから必要な依存性が注入されます。

## 3. 登録済みサービスと実装例

以下は、`di_container.py` における主要なサービスの登録例です。

```python
# /github_broker/infrastructure/di_container.py (抜粋)

from __future__ import annotations

from typing import cast

import punq
import redis

from github_broker.application.task_service import TaskService
from github_broker.domain.agent_config import AgentConfigList
from github_broker.infrastructure.agent.loader import AgentConfigLoader
from github_broker.infrastructure.config import Settings, get_settings
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient


def create_container(settings: Settings | None = None) -> punq.Container:
    s = settings or get_settings()

    # Parse owner and repo from repository string
    try:
        owner, repo_name = s.github_agent_repository.split("/")
    except ValueError:
        raise ValueError(
            "github_agent_repository must be in the format 'owner/repo_name'"
        ) from None

    # 各種クライアントのインスタンス化
    github_client = GitHubClient(
        github_repository=s.github_agent_repository,
        github_token=s.github_personal_access_token,
    )
    redis_instance = redis.from_url(s.redis_url, decode_responses=True)
    redis_client = RedisClient(redis=redis_instance, owner=owner, repo_name=repo_name)

    # エージェント設定のロード
    agent_config_loader = AgentConfigLoader()
    agent_definitions = agent_config_loader.load_from_file(s.github_agent_config_file)

    # コンテナの構築と登録
    container = punq.Container()
    container.register(Settings, instance=s)
    container.register(GitHubClient, instance=github_client)
    container.register(RedisClient, instance=redis_client)
    container.register(AgentConfigLoader, instance=agent_config_loader)
    container.register(AgentConfigList, instance=cast(AgentConfigList, agent_definitions))

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
    事前にインスタンス化して `instance=` で登録するパターンを推奨します。

    ```python
    # github_broker/infrastructure/di_container.py
    # 必要なインポートを追加
    from github_broker.application.analytics_service import NewAnalyticsService

    def create_container(settings: Settings | None = None) -> punq.Container:
        ...
        # サービスをコンテナに登録（インスタンスを生成して登録するパターン）
        new_analytics_service = NewAnalyticsService(...)
        container.register(NewAnalyticsService, instance=new_analytics_service)
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