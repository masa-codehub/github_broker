# 概要 / Summary
[ADR-004] punq DIコンテナの実装パターン

## 状況 / Context

## Status

**Context:**

ADR 002に基づく設定管理のリファクタリングにおいて、DIコンテナライブラリ`punq`を導入した際、依存関係の解決で複数のテストが長時間にわたり失敗し続けた。特に、`container.resolve(TaskService)`を呼び出す過程で、`TypeError: missing required positional argument`や`punq.InvalidRegistrationError`といったエラーが頻発した。

**Investigation:**

当初、`punq`がファクトリ関数の引数（例: `def my_factory(settings: Settings)`)を、コンテナに登録されている他のサービス（この場合は`Settings`）を使って自動的に解決してくれるものと期待していた。この仮説に基づき、`@container.register`デコレータや`container.register(factory=...)`といったアプローチを試したが、すべて失敗に終わった。

エラーメッセージを詳細に分析した結果、`punq`の自動解決（オートワイヤリング）は、主に**クラスのコンストラクタ（`__init__`）の型ヒント**に基づいて機能し、ファクトリ関数の引数に対しては再帰的な依存性解決を自動的には行わないことが判明した。

## 決定 / Decision

`punq`の挙動を誤解しない、最も確実で明示的な実装パターンを採用する。

1.  **依存される基本オブジェクトから登録する:** 依存関係のツリーの末端にあたるオブジェクト（例: `Settings`や、プリミティブなライブラリのインスタンスである`Redis`）を、まずコンテナに登録する。この際、必要であればファクトリ関数を用いる。

2.  **依存するクラスは直接登録する:** 上記の基本オブジェクトに依存するサービスクラス（例: `RedisClient`や`TaskService`）は、ファクトリを定義せず、**クラスそのもの**をコンテナに登録する。

これにより、`punq`は各クラスのコンストラクタの型ヒント（例: `__init__(self, redis: Redis)`)を読み取り、コンテナ内から対応する型（`Redis`）のインスタンスを自動的に見つけて注入する。この方法が、`punq`の機能を最も素直に利用した、予測可能で堅牢なパターンであると結論付けた。

**最終的な`di_container.py`の実装例:**
```python
import punq
from redis import Redis
from .config import Settings
# ... other imports

def create_container() -> punq.Container:
    container = punq.Container()

    # 1. 基本的なオブジェクトを登録
    container.register(Settings, scope=punq.Scope.singleton)

    def redis_factory(settings: Settings) -> Redis:
        return Redis(host=settings.REDIS_HOST, ...)
    container.register(Redis, factory=redis_factory)

    # 2. 上記に依存するクラスを直接登録
    container.register(RedisClient) # __init__(self, redis: Redis) を見てくれる
    container.register(GitHubClient) # __init__(self, settings: Settings) を見てくれる
    container.register(TaskService) # __init__(self, redis_client: RedisClient, ...) を見てくれる

    return container
```

## 結果 / Consequences

## Consequences

- **Pro:** 依存関係の構築方法が明確になり、コンテナの挙動が予測しやすくなる。`punq`の「魔法」に頼りすぎないため、デバッグが容易になる。
- **Pro:** 新しいサービスを追加する際も、このパターンに従うことで、同様の問題の再発を防げる。
- **Con:** 依存関係が非常に複雑な場合、`di_container.py`が少し長くなる可能性があるが、その明示性がリスクを上回るメリットとなる。

## Implementation Status (実装状況)

完了