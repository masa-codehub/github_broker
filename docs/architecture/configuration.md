# 設定管理 (`Settings`) 設計書

## 1. 概要

このドキュメントは、`github_broker`アプリケーションにおける設定管理の仕組みについて説明します。
本プロジェクトでは、`Pydantic`の`BaseSettings`クラスを利用して、環境変数と設定ファイル(`agents.yml`)から設定値を読み込み、`Settings`クラスとしてアプリケーション全体に提供します（ADR-002, ADR-013）。

設定の定義は `github_broker/infrastructure/config.py` に、エージェントの役割定義はリポジトリルートの `agents.yml` にあります。

## 2. 設定の優先順位

`Settings`クラスは、以下の優先順位で設定値を解決します。

1.  **環境変数:** 最も高い優先度を持ちます。デプロイ環境ごとに異なる値（APIキーなど）を設定するために使用します。
2.  **`.env`ファイル:** ローカル開発用に、プロジェクトルートの`.env`ファイルに記述された値を読み込みます。
3.  **`agents.yml`ファイル:** エージェントの役割定義など、構造化された設定をファイルから読み込みます。
4.  **`Settings`クラスのデフォルト値:** 上記のいずれでも指定されなかった場合のデフォルト値です。

## 3. 設定項目一覧

### 3.1. 環境変数

アプリケーションの実行には、以下の環境変数の設定が必要です。

| 環境変数名           | 型        | 説明                                                         | 設定例                                   |
| :------------------- | :-------- | :----------------------------------------------------------- | :--------------------------------------- |
| `GITHUB_TOKEN`       | `SecretStr` | GitHub APIにアクセスするためのPersonal Access Token。         | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `REDIS_URL`          | `str`       | 接続先のRedisサーバーのURL。                                 | `redis://localhost:6379/0`               |
| `GEMINI_API_KEY`     | `SecretStr` | Google Gemini APIを利用するためのAPIキー。                   | `AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`    |
| `GITHUB_REPOSITORY`  | `str`       | 操作対象のGitHubリポジトリ名 (`owner/repo`形式)。現状では単一リポジトリのみサポート。将来的に複数リポジトリ対応 (`ADR-005`) のための拡張が可能です。 | `masa-codehub/github_broker`               |

### 3.2. `agents.yml`

エージェントの役割（Role）と能力（Capabilities）を定義します。DIコンテナは、このファイルを読み込んで`AgentConfigList`オブジェクトを生成します。

#### フォーマット

```yaml
agents:
  - role: "BACKEND_CODER"
    description: "バックエンドのコードを記述するエージェント"
    capabilities:
      - "python"
      - "api"
      - "database"

  - role: "TECHNICAL_DESIGNER"
    description: "技術的な設計ドキュメントを作成するエージェント"
    capabilities:
      - "markdown"
      - "mermaid"
      - "c4-model"
```

## 4. アプリケーションでの利用

`Settings`クラスは、DIコンテナ (`di_container.py`) によってシングルトンとして登録されます。
`TaskService`などの他のサービスは、コンストラクタで`Settings`を型ヒント付きで受け取ることで、設定値にアクセスできます。

```python
# /github_broker/application/task_service.py (抜粋)

class TaskService:
    def __init__(self, settings: Settings, ...) -> None:
        self.settings = settings
        # self.settings.github_token などでアクセス可能
```
