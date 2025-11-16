# 【Task】TaskServiceの単体テストを修正・追加する

## 親Issue (Parent Issue)
- #1693

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

## Issue: #1703
## Status: Open

# 目的とゴール / Purpose and Goals
`TaskService` のリファクタリングに伴い、単体テストを新しい仕様に適応させ、コードの品質と動作の正当性を保証する。

## As-is (現状)
`TaskService` の単体テストが、古い実装（ハードコードされた役割）に依存している。

## To-be (あるべき姿)
`TaskService` の単体テストが、新しいDIベースの実装に対応するように修正され、動的な設定に基づいたテストケースが追加されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `tests/application/test_task_service.py` を編集する。
2. `TaskService` のインスタンス化を行っている部分を修正し、テスト用のエージェント設定リストを注入するように変更する。
3. 注入した設定に基づいて、タスクの割り当てが正しく行われることを検証するテストケースを追加する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- `TaskService` のテストが、DIを通じて注入された設定を使ってパスすること。

## 成果物 (Deliverables)
- `tests/application/test_task_service.py` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/refactor-task-service-for-external-config`
- **作業ブランチ (Feature Branch):** `task/update-task-service-tests`

## 子Issue (Sub-Issues)
