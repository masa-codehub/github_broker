# 設定管理 (`Settings`) 設計書

## 1. 概要

このドキュメントは、`github_broker`アプリケーションにおける設定管理の仕組みについて説明します。
本プロジェクトでは、`Pydantic`の`BaseSettings`クラスを利用して、環境変数と`.env`ファイルから設定値を読み込み、`Settings`クラスとしてアプリケーション全体に提供します（ADR-002, ADR-013）。

設定の定義は `github_broker/infrastructure/config.py` に、エージェントの役割定義はリポジトリルートの `agents.yml` にあります。

## 2. 設定の優先順位

`Settings`クラスは、以下の優先順位で設定値を解決します。

1.  **環境変数:** 最も高い優先度を持ちます。デプロイ環境ごとに異なる値（APIキーなど）を設定するために使用します。
2.  **`.env`ファイル:** ローカル開発用に、プロジェクトルートの`.env`ファイルに記述された値を読み込みます。
3.  **`Settings`クラスのデフォルト値:** 上記のいずれでも指定されなかった場合のデフォルト値です。

※ `agents.yml`は`Settings`クラスではなく、`AgentConfigLoader`によって別途読み込まれます。

## 3. 設定項目一覧

### 3.1. 環境変数

アプリケーションの実行には、以下の環境変数の設定が必要です。

| 環境変数名                     | 型          | 説明                                                         | 設定例                                   |
| :----------------------------- | :---------- | :----------------------------------------------------------- | :--------------------------------------- |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | `SecretStr` | GitHub APIにアクセスするためのPersonal Access Token。         | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `REDIS_URL`                    | `str`       | 接続先のRedisサーバーのURL。                                 | `redis://localhost:6379/0`               |
| `GOOGLE_API_KEY`               | `SecretStr` | Google Gemini APIを利用するためのAPIキー。                   | `AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`    |
| `GITHUB_AGENT_REPOSITORY`      | `str`       | 操作対象のGitHubリポジトリ名 (`owner/repo`形式)。現状では単一リポジトリのみサポート。将来的に複数リポジトリ対応 (`ADR-005`) のための拡張が可能です。 | `masa-codehub/github_broker`             |
| `GITHUB_APP_ID`                | `str`       | GitHub AppのApp ID。                                         | `123456`                                 |
| `GITHUB_APP_PRIVATE_KEY`       | `SecretStr` | GitHub AppのPrivate Key（PEM形式の文字列。改行はエスケープして格納）。 | `-----BEGIN PRIVATE KEY-----
...`       |
| `GITHUB_WEBHOOK_SECRET`        | `SecretStr` | GitHub Webhookの署名検証に利用するシークレット。             | `xxxxxxxxxxxxxxxxxxxxxxxxxxxx`           |

### 3.2. `agents.yml`

エージェントの役割（Role）とペルソナ（Persona）を定義します。DIコンテナは、このファイルを読み込んで`AgentConfigList`オブジェクトを生成します。

#### フォーマット

```yaml
agents:
  - role: PRODUCT_MANAGER
    persona: "プロダクトの全体的なビジョンやビジネス目標を提示し、具体的な開発タスク（GitHub Issues）に分解します。"

  - role: BACKENDCODER
    persona: "バックエンドの機能実装、API開発、データベース連携などを担当します。"
```

## 4. アプリケーションでの利用

DIコンテナは`Settings`を用いて`GitHubClient`や`RedisClient`、`AgentConfigList`などの依存オブジェクトを初期化し、`TaskService`などのサービスにはそれらをコンストラクタインジェクションで渡します。

```python
# /github_broker/application/task_service.py (抜粋)

class TaskService:
    def __init__(
        self,
        github_client: GitHubClient,
        redis_client: RedisClient,
        agent_configs: AgentConfigList,
    ) -> None:
        self.github_client = github_client
        self.redis_client = redis_client
        self.agent_roles = {agent.role for agent in agent_configs.get_all()}
```