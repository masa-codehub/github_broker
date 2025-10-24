# 【Story】タスク候補のフィルタリングロジックを実装する

## 親Issue (Parent Issue)
- #1737

## 子Issue (Sub-Issues)
- #1744

## Issue: #1739
## Status: Open

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/015-strict-priority-bucket-assignment.md`

# 目的とゴール / Purpose and Goals
特定された最高優先度レベルのラベルを持つIssueのみをタスク割り当ての候補とするフィルタリングロジックを実装する。

## As-is (現状)
タスク割り当てロジックは、優先度レベルに関わらずすべての割り当て可能なIssueを候補としている。

## To-be (あるべき姿)
`TaskService`が、特定された最高優先度レベルのラベルを持つIssueのみをタスク割り当ての候補としてフィルタリングできるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: 特定された最高優先度レベルのラベルを持つIssueのみをフィルタリングするロジックを実装する`

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。
- 最高優先度以外のIssueが候補リストから除外されること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` (更新)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-015`
- **作業ブランチ (Feature Branch):** `story/implement-task-filtering-logic`
