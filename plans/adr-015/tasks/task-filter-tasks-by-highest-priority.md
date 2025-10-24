# 【Task】特定された最高優先度レベルのラベルを持つIssueのみをフィルタリングするロジックを実装する

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/015-strict-priority-bucket-assignment.md`

# 目的とゴール / Purpose and Goals
タスク割り当ての候補となるIssueを、現在の最高優先度レベルに限定するフィルタリングロジックを実装する。

## As-is (現状)
タスク割り当てロジックは、優先度レベルに関わらずすべての割り当て可能なIssueを候補としている。

## To-be (あるべき姿)
`TaskService`内に、最高優先度レベルのラベルを持つIssueのみをタスク割り当ての候補としてフィルタリングする関数が実装されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py`内に、Issueリストと最高優先度レベルを受け取り、フィルタリングされたIssueリストを返す関数を実装する。
2. 優先度ラベルの比較ロジックを正確に実装する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- 最高優先度以外のIssueが候補リストから正確に除外されること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/implement-task-filtering-logic`
- **作業ブランチ (Feature Branch):** `task/filter-tasks-by-highest-priority`
