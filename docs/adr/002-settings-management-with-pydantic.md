# 概要 / Summary
[ADR-002] 設定管理のリファクタリングとDocker Secretsへの移行

- Status: Accepted
- Date: 2025-11-14

## 状況 / Context

現在、システムの様々な設定値（APIキー、接続情報など）が、`os.getenv()` を通じてコードの複数箇所で直接読み込まれています。特に `GITHUB_TOKEN` や `GEMINI_API_KEY` などの機密情報が `docker-compose.yml` 内にプレーンテキストの環境変数として記述されており、セキュリティ上のリスクとなっています。また、設定の参照箇所が分散しているため、管理性や保守性が低い状態です。

この問題を解決するため、設定管理の方法をリファクタリングし、機密情報をより安全な方法で扱う必要があります。

## 決定 / Decision

設定管理ライブラリとして `pydantic-settings` を導入し、設定情報を一元管理するクラスを設けます。機密情報は Docker Secrets を利用してコンテナに安全に提供します。

### 1. `pydantic-settings` の導入

`pydantic-settings` は、Pydanticモデルを利用して環境変数やSecretsファイルから設定を型安全に読み込むことができるライブラリです。これにより、設定の定義と利用を分離し、コードの可読性と保守性を向上させます。

### 2. `Settings` クラスの設計

`github_broker/infrastructure/config.py` に以下の `Settings` クラスを新設します。

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Pydantic-settingsの設定
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Docker Secretsのパスを指定
        secrets_dir="/run/secrets" if os.path.exists("/.dockerenv") else None,
        extra="ignore"
    )

    # 機密情報 (Docker Secretsから読み込む)
    GITHUB_TOKEN: str
    GEMINI_API_KEY: str

    # 一般的な設定 (環境変数から読み込む)
    BROKER_PORT: int = 8000
    GITHUB_REPOSITORY: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    TESTING: bool = False

# シングルトンインスタンス
settings = Settings()
```

### 3. `docker-compose.yml` の変更案

`docker-compose.yml` を以下のように変更し、`environment` から機密情報を削除し、`secrets` を利用するようにします。

**変更前:**
```yaml
services:
  github_broker:
    # ...
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN:-my_github_token}
      - GEMINI_API_KEY=${GEMINI_API_KEY:-my_gemini_api_key}
      # ...
```

**変更後:**
```yaml
services:
  github_broker:
    # ...
    environment:
      - GITHUB_REPOSITORY=${GITHUB_REPOSITORY:-my_account/my_repository}
      - REDIS_HOST=redis
      # ...
    secrets:
      - github_token
      - gemini_api_key

secrets:
  github_token:
    file: ./secrets/github_token
  gemini_api_key:
    file: ./secrets/gemini_api_key
```
ローカル開発用に、プロジェクトルートに `secrets/` ディレクトリを作成し、その中に `github_token` などのファイル名で機密情報を記述します。

### 4. DIコンテナによる `Settings` の注入

`github_broker/infrastructure/di_container.py` を変更し、`Settings` のシングルトンインスタンスを各コンポーネントに注入します。

```python
# github_broker/infrastructure/di_container.py

from .config import settings
from .redis_client import RedisClient
# ... 他のimport

class DiContainer:
    def __init__(self):
        self.settings = settings
        self.redis_client = RedisClient(
            host=self.settings.REDIS_HOST,
            port=self.settings.PORT,
            db=self.settings.REDIS_DB
        )
        # ... 他のクライアントも同様にsettingsオブジェクトから設定を渡す
```

これにより、`os.getenv()` を直接呼び出す必要がなくなり、すべての設定が `di_container.settings` を通じて型安全に参照できるようになります。

## 結果 / Consequences

### メリット (Positive consequences)
- **セキュリティ向上:** 機密情報がコードや `docker-compose.yml` から分離され、Docker Secretsによって安全に管理されるようになります。
- **保守性向上:** 設定が一元管理されるため、変更や追加が容易になります。
- **開発効率向上:** 型安全な設定アクセスにより、設定名のタイポなどのヒューマンエラーを防ぐことができます。

### デメリット (Negative consequences)
- **依存ライブラリの追加:** `pydantic-settings` への依存が新たに追加されます。

## 検証基準 / Verification Criteria

## 実装状況 / Implementation Status

完了
