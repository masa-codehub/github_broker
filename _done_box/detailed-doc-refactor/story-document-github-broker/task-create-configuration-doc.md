---
title: "【Task】設定管理ドキュメント `configuration.md` を新規作成"
labels: ["task", "documentation", "refactoring", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】設定管理ドキュメント `configuration.md` を新規作成

## 親Issue (Parent Issue)
- (Story: `github_broker`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `reqs/adr/002-settings-management-with-pydantic.md`
- `reqs/adr/013-agent-role-configuration.md`

## As-is (現状)
- `Settings`クラス (`config.py`) や `agents.yml` といった、アプリケーションの動作を決定する重要な設定の仕組みについて、まとまったドキュメントが存在しない。
- 環境変数で何を設定すべきか、`agents.yml` にどう役割を定義するかが不明確である。

## To-be (あるべき姿)
- `docs/architecture/configuration.md`が新規作成される。
- このドキュMントには、以下の内容が網羅的に記述されている。
  1. Pydantic `BaseSettings` を利用した、環境変数からの設定値の読み込み方法。
  2. アプリケーションが必要とする環境変数の一覧とその説明。
  3. `agents.yml` のフォーマットと、エージェントの役割・能力を定義する方法。
  4. `Settings` クラスがDIコンテナを通じて、どのようにアプリケーション全体に共有されるかの概要。

## ユーザーの意図と背景の明確化
- ユーザーは、アプリケーションの設定方法をブラックボックスではなく、明確な仕様としてドキュメント化したいと考えている。これにより、開発者や運用者がアプリケーションをデプロイ・設定する際のミスを減らし、新しい設定項目の追加を容易にすることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `docs/architecture/configuration.md` (新規作成)
- **修正方法:** 以下の内容でファイルを**新規作成**する。

```markdown
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
```

## 完了条件 (Acceptance Criteria)
- `docs/architecture/configuration.md` が、上記の「具体的な修正内容」で新規作成されていること。

## 成果物 (Deliverables)
- 新規作成された `docs/architecture/configuration.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/create-configuration-doc`
