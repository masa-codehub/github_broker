# 【Task】開発者ガイドに新しいタスク割り当てルールに関する説明を追記する

## 親Issue (Parent Issue)
- #1755

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/015-strict-priority-bucket-assignment.md`

## Issue: #1756
## Status: Open

# 目的とゴール / Purpose and Goals
ADR-015で導入された厳格な優先度バケットによるタスク割り当てについて、開発者ガイドに説明を追記し、開発者がルールを理解できるようにする。

## As-is (現状)
開発者ガイドに新しいタスク割り当てルールに関する記述がない。

## To-be (あるべき姿)
開発者ガイドに、新しいタスク割り当てルールに関する明確な説明が追記されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. 関連する開発者ガイド（例: `docs/guides/development-workflow.md`など）を特定する。
2. 新しいタスク割り当てルールについて、具体的な例を交えながら説明を追記する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- 開発者ガイドが新しいタスク割り当てルールを正確に反映していること。

## 成果物 (Deliverables)
- 開発者ガイド (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-adr-015-changes`
- **作業ブランチ (Feature Branch):** `task/update-dev-guide-with-priority-rules`
