# 【Task】開発者ガイドに、agents.ymlとAGENT_CONFIG_PATHに関する説明を追記する

## 親Issue (Parent Issue)
- #1694

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

## Issue: #1704
## Status: Open

# 目的とゴール / Purpose and Goals
開発者が新しいエージェント設定方法を理解し、プロジェクトを正しくセットアップできるよう、関連ドキュメントを更新する。

## As-is (現状)
開発者向けドキュメントに、新しいエージェント設定方法に関する記述がない。

## To-be (あるべき姿)
`README.md` や `docs/guides/getting-started.md` などの関連ドキュメントに、`agents.yml` のフォーマットと `AGENT_CONFIG_PATH` 環境変数の役割について、明確な説明が追記されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. 関連するドキュメントファイルを特定する。
2. 新しい設定方法について、開発者が容易に理解できるような説明を追記する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- ドキュメントの変更が、他の開発者にとって分かりやすいものであること。

## 成果物 (Deliverables)
- `README.md` (更新の可能性あり)
- `docs/guides/getting-started.md` (更新の可能性あり)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/update-docs-for-agent-config`
- **作業ブランチ (Feature Branch):** `task/document-new-agent-config`
## 子Issue (Sub-Issues)
