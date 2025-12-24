# CI/CD 環境とワークフロー

このドキュメントは、本プロジェクトの継続的インテグレーション（CI）ワークフローの概要と、それが実行される環境について説明します。

ワークフローの定義は `.github/workflows/ci.yml` にあります。

## 1. CIのトリガー (Triggers)

ADR-011に基づき、CIワークフローはすべてのPull Requestに対してトリガーされます。具体的には、以下のいずれかのアクションを伴う場合に実行されます。

-   `opened`
-   `synchronize` (新しいコミットがプッシュされた場合)
-   `reopened`
-   `ready_for_review`

現在、特定のファイルパスによる実行の除外（`paths-ignore`）は設定されておらず、**すべてのファイル変更がCIの対象となります。**

## 2. 実行環境 (Runner Environment)

CIジョブは、以下のラベルを持つセルフホストランナー上で実行されます。

-   **`runs-on`:** `[self-hosted]`

実行環境の詳細は以下の通りです。

-   **Labels:** `self-hosted`, `linux`, `x64`, `gpu`
-   **Operating System:** Ubuntu 24.04
-   **Host Environment:** ランナーは `github_broker-github_runner` イメージを使用した `github-runner` コンテナ内でホストされています。

ワークフローのYAMLを編集する際は、このラベルを指定する必要があります。

```
jobs:
  test:
    runs-on: [self-hosted]
    # ...
```

## 3. CIワークフローの主要ステップ

`test`ジョブでは、以下の主要なステップが実行されます。

1.  **チェックアウト:**
    `actions/checkout@v4` を使用して、リポジトリのソースコードをチェックアウトします。

2.  **Python環境のセットアップ:**
    `actions/setup-python@v5` を使用して、`3.13.3` バージョンのPython環境をセットアップします。`pip`のキャッシュが有効になっており、ビルド時間を短縮します。

3.  **依存関係のインストール:**
    `pip install -e .[test,dev]` と `pip install -e ./issue_creator_kit` を実行し、プロジェクト本体および開発・テストに必要な全ての依存ライブラリをインストールします。

4.  **品質チェックの統合実行 (ADR-010):**
    `pre-commit run --all-files` を実行します。これにより、以下のチェックが統合的に行われます。
    -   **Linting & Formatting:** `ruff` によるコード整形と静的解析。
    -   **Unit & Integration Tests:** `pytest` による単体・統合テストの実行。
    -   **Type Checking:** `mypy` による型チェック。
    -   **Document Validation:** カスタムスクリプトによるドキュメントフォーマットの検証。

5.  **サーバー起動テスト:**
    `broker_main.py` をバックグラウンドで起動し、`/health` エンドポイントにcURLでアクセスできることを確認します。これにより、依存関係の解決や基本的な設定に問題がなく、アプリケーションが正常に起動できることを検証します。

6.  **カバレッジレポートのアップロード:**
    すべてのチェックが成功した場合（ワークフローが成功した場合）、`coverage.xml` がアーティファクトとしてアップロードされ、後からカバレッジレポートを確認できます。