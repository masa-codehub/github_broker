---
title: "【Task】`di-container.md`を最新の実装に同期し、設計意図を追記"
labels: ["task", "documentation", "refactoring", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】`di-container.md`を最新の実装に同期し、設計意図を追記

## 親Issue (Parent Issue)
- (Story: `github_broker`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `reqs/adr/004-punq-di-pattern.md`

## As-is (現状)
- `docs/architecture/di-container.md`のサンプルコードや説明が、現在の`github_broker/infrastructure/di_container.py`の実装と一致していない。
- `di_container.py`に実装されているコンポーネント単位での登録（`register_broker_service`等）という設計意図や、開発者が新しいサービスを追加する際の具体的なガイドラインがドキュメント化されていない。

## To-be (あるべき姿)
- `di-container.md`に、`di_container.py`の実装とADR-004の決定事項が反映される。
- なぜコンポーネント単位で登録するのかという設計思想と、新しいサービスを追加する際の手順が明記され、開発者が安全にコンテナを拡張できるようになる。

## ユーザーの意図と背景の明確化
- ユーザーは、DIコンテナの利用方法が属人化することを懸念している。ドキュメントに明確なガイドラインを設けることで、誰でも一貫した方法で依存性追加を行えるようにし、メンテナンス性を向上させることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `docs/architecture/di-container.md`
- **修正方法:** ファイル全体を以下の内容で**上書き**する。

```markdown
# 依存性注入(DI)コンテナ 設計書

## 1. 概要

このドキュメントは、`github_broker`プロジェクトにおける依存性注入（DI）の設計と実装について説明します。
本プロジェクトでは、コンポーネント間の依存関係を疎結合に保ち、テスト容易性を向上させる目的で、軽量なDIコンテナライブラリ `punq` を採用しています (ADR-004)。

依存関係の定義は、すべて `/github_broker/infrastructure/di_container.py` に一元管理されています。

## 2. 設計思想と登録方針

### コンポーネント単位での登録

`di_container.py` では、`register_broker_service()` や `register_issue_creator_kit()` といった関数を通じて、コンポーネント単位で依存性を登録する方針を採っています。

これは、各コンポーネントが必要とする依存性を一つの関数内にカプセル化することで、見通しを良くし、関心事の分離を徹底するためです。将来的に特定のコンポーネントを無効化したり、別の実装に差し替える際に、この関数単位での操作が可能となり、メンテナンス性が向上します。

### ライフサイクル

- **`scope="singleton"`**: アプリケーション全体で単一のインスタンスを共有するサービス（例: `Settings`, `GithubClient`, `RedisClient`）に対して使用します。
- **`scope="transient"`** (または指定なし): リクエストごと、または呼び出しごとに新しいインスタンスが必要なサービス（例: `TaskService`）に対して使用します。

原則として、ステートレスなサービスは `singleton`、状態を持つ可能性があるサービスは `transient` とすることを推奨します。

## 3. 登録済みサービスと実装例

以下は、`di_container.py` における主要なサービスの登録例です。

```python
# /github_broker/infrastructure/di_container.py (抜粋)

import punq

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.config import Settings
from github_broker.infrastructure.gemini_client import GeminiClient
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient

def register_broker_service(container: punq.Container) -> None:
    """github_brokerのコアサービスの依存性を登録します。"""

    # 設定クラスは最初にシングルトンで登録
    container.register(Settings, scope=punq.Scope.singleton)
    settings = container.resolve(Settings)

    # 各種クライアントをシングルトンで登録
    container.register(
        GitHubClient,
        instance=GitHubClient(settings.github_token),
        scope=punq.Scope.singleton,
    )
    container.register(
        RedisClient,
        instance=RedisClient(settings.redis_url),
        scope=punq.Scope.singleton,
    )
    container.register(
        GeminiClient,
        instance=GeminiClient(settings.gemini_api_key),
        scope=punq.Scope.singleton,
    )

    # TaskServiceはリクエストごとに生成
    container.register(TaskService)

# DIコンテナの初期化と登録の実行
container = punq.Container()
register_broker_service(container)
```

## 4. 開発ガイドライン：新しいサービスの追加方法

新しいサービス（例: `NewAnalyticsService`）を追加し、それを `TaskService` に注入する場合、以下の手順に従ってください。

1.  **サービスの登録:**
    `github_broker/infrastructure/di_container.py` の `register_broker_service()` 関数内に、`NewAnalyticsService` の登録処理を追記します。シングルトンが適切であれば `scope` を指定します。

    ```python
    # github_broker/infrastructure/di_container.py

    def register_broker_service(container: punq.Container) -> None:
        ...
        container.register(NewAnalyticsService, scope=punq.Scope.singleton) # この行を追加
        ...
    ```

2.  **依存性の注入:**
    `TaskService` のコンストラクタで、`NewAnalyticsService` を型ヒントと共に引数として受け取ります。DIコンテナが自動的にインスタンスを注入します。

    ```python
    # github_broker/application/task_service.py

    class TaskService:
        def __init__(self, github_client: GitHubClient, ..., new_service: NewAnalyticsService) -> None:
            self._github_client = github_client
            ...
            self._new_service = new_service
    ```
このように、依存関係の変更は `di_container.py` 内で完結するため、アプリケーションの他の部分への影響を最小限に抑えることができます。

```

## 完了条件 (Acceptance Criteria)
- `docs/architecture/di-container.md` が、上記の「具体的な修正内容」で上書きされていること。

## 成果物 (Deliverables)
- 更新された `docs/architecture/di-container.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/update-di-container-doc`