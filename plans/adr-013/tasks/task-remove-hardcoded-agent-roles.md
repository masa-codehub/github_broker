# 【Task】TaskService内のハードコードされたAGENT_ROLESを削除し、インジェクションされた設定を利用するロジックに置き換える

## 親Issue (Parent Issue)
- #1693

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

## Issue: #1702
## Status: Open

# 目的とゴール / Purpose and Goals
`TaskService` からハードコードされた役割定義を完全に排除し、外部から注入された動的な設定のみを利用するようにリファクタリングする。

## As-is (現状)
`TaskService` が、内部にハードコードされた `AGENT_ROLES` クラス変数を使って、タスク割り当て対象のラベルを判断している。

## To-be (あるべき姿)
`TaskService` が、コンストラクタで注入されたエージェント定義リストを動的に参照し、タスク割り当ての判断を行うようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py` を編集する。
2. `AGENT_ROLES` クラス変数を削除する。
3. 役割をチェックしているロジックを、インスタンス変数 `self.agent_definitions` に含まれる `role` を参照するように修正する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- `TaskService` から `AGENT_ROLES` が完全に削除されていること。
- 注入された設定に基づいて、Issueのラベルを正しく判定できること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/refactor-task-service-for-external-config`
- **作業ブランチ (Feature Branch):** `task/remove-hardcoded-agent-roles`