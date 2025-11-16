# 【Task】TaskService内のタスク割り当てロジックを修正し、フィルタリングされた候補リストを使用するように変更する

## 親Issue (Parent Issue)
- #1740

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/015-strict-priority-bucket-assignment.md`

## Issue: #1745
## Status: Open

# 目的とゴール / Purpose and Goals
`TaskService`のタスク割り当てロジックを修正し、最高優先度レベルでフィルタリングされたIssueリストのみを考慮してタスクを割り当てるように変更する。

## As-is (現状)
`TaskService`のタスク割り当てロジックは、フィルタリングされていないIssueリストを基にタスクを割り当てている。

## To-be (あるべき姿)
`TaskService`が、最高優先度レベルでフィルタリングされたIssueリストのみを考慮してタスクを割り当て、厳格な優先度バケット方式を強制するようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py`内のタスク割り当て関数を特定する。
2. この関数が、フィルタリングされたIssueリストを受け取るように修正する。
3. フィルタリングされたリストからタスクを選択し、割り当てるロジックを実装する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- フィルタリングされた候補リストに基づいてのみタスクが割り当てられること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/update-task-assignment-logic`
- **作業ブランチ (Feature Branch):** `task/update-task-assignment-logic`

## 子Issue (Sub-Issues)
