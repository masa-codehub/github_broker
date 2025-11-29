---
title: "【Task】`ci-cd-environment.md`を現在の`ci.yml`と完全に同期"
labels: ["task", "documentation", "refactoring", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】`ci-cd-environment.md`を現在の`ci.yml`と完全に同期

## 親Issue (Parent Issue)
- (Story: `github_broker`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `reqs/adr/010-ci-cd-process-improvement.md`
- `reqs/adr/011-trigger-ci-on-all-branches.md`

## As-is (現状)
- `docs/architecture/ci-cd-environment.md`の内容が、`.github/workflows/ci.yml`の実際の実装と大きく乖離している。
  - **トリガー条件:** ドキュメントでは「ドキュメントのみの変更ではスキップ」とあるが、実装では全ファイル変更でトリガーされている。
  - **`runs-on`ラベル:** ドキュメントと実装で指定されているラベルが一致しない。
  - **ジョブ内容:** 実装されている具体的なCIステップ（依存関係インストール、pre-commit実行、サーバー起動テスト等）がドキュメントに記載されていない。

## To-be (あるべき姿)
- `ci-cd-environment.md`が、`ci.yml`で定義されているトリガー条件、`runs-on`ラベル、ジョブの各ステップを正確に反映した内容になる。
- 開発者がこのドキュメントを読むだけで、CIプロセスで何が実行され、どのような設定になっているかを完全に理解できる。

## ユーザーの意図と背景の明確化
- ユーザーは、CI/CDというプロジェクトの品質を担保する重要なプロセスが、ドキュメントと実装で一致していることを求めている。これにより、CIの挙動を予測しやすくなり、ワークフローのメンテナンスや改善が容易になることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `docs/architecture/ci-cd-environment.md`
- **修正方法:** ファイル全体を以下の内容で**上書き**する。

```markdown
# CI/CD 環境とワークフロー

このドキュメントは、本プロジェクトの継続的インテグレーション（CI）ワークフローの概要と、それが実行される環境について説明します。

ワークフローの定義は `.github/workflows/ci.yml` にあります。

## 1. CIのトリガー (Triggers)

CIワークフローは、Pull Requestが以下のいずれかのアクションを伴う場合にトリガーされます（ADR-011）。

-   `opened`
-   `synchronize` (新しいコミットがプッシュされた場合)
-   `reopened`
-   `ready_for_review`

現在、特定のファイルパスによる実行の除外（`paths-ignore`）は設定されておらず、**すべてのファイル変更がCIの対象となります。**

## 2. 実行環境 (Runner Environment)

CIジョブは、以下のラベルを持つセルフホストランナー上で実行されます。

-   **`runs-on`:** `[self-hosted]`

ワークフローのYAMLを編集する際は、このラベルを指定する必要があります。

```yaml
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
    `actions/setup-python@v5` を使用して、`3.13` バージョンのPython環境をセットアップします。`pip`のキャッシュが有効になっており、ビルド時間を短縮します。

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
    テストが成功した場合、`coverage.xml` がアーティファクトとしてアップロードされ、後からカバレッジレポートを確認できます。
```

## 完了条件 (Acceptance Criteria)
- `docs/architecture/ci-cd-environment.md` が、上記の「具体的な修正内容」で上書きされていること。

## 成果物 (Deliverables)
- 更新された `docs/architecture/ci-cd-environment.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/update-ci-cd-doc`