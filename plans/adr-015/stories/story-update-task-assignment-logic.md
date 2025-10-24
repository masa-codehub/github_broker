# 【Story】タスク割り当てロジックを更新する

## 親Issue (Parent Issue)
- (Epic起票後に追記)

## 子Issue (Sub-Issues)
- (Task起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/015-strict-priority-bucket-assignment.md`

# 目的とゴール / Purpose and Goals
フィルタリングされた最高優先度の候補リストの中から、現在作業中でないIssueをエージェントに割り当てるように、既存のタスク割り当てロジックを更新する。

## As-is (現状)
`TaskService`のタスク割り当てロジックは、フィルタリングされていないIssueリストを基にタスクを割り当てている。

## To-be (あるべき姿)
`TaskService`が、最高優先度レベルでフィルタリングされたIssueリストのみを考慮してタスクを割り当て、厳格な優先度バケット方式を強制するようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: TaskService`内のタスク割り当てロジックを修正し、フィルタリングされた候補リストを使用するように変更する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。
- フィルタリングされた候補リストに基づいてのみタスクが割り当てられること。

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
- **作業ブランチ (Feature Branch):** `story/update-task-assignment-logic`
