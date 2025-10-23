# 目的とゴール
# Issue: #1523
Status: COMPLETED
# 目的とゴール / Purpose and Goals

## 親Issue (Parent Issue)
- #1521

## 子Issue (Sub-Issues)
- #1527

## As-is (現状)
レビュー対象Issueの検索クエリが最適化されておらず、検出後すぐにタスクとしてクライアントに割り当てられてしまう。

## To-be (あるべき姿)
`TaskService`において、レビュー対象Issueの検索クエリが`is:issue label:needs-review linked:pr is:open`に更新される。また、Issueが検出されてから一定時間（5分）が経過した後にのみ、タスクとしてクライアントに割り当てられる遅延処理が実装される。

## 完了条件 (Acceptance Criteria)
- [ ] Task: `TaskService`を修正し、レビューIssueの検索クエリを更新し、遅延処理を実装する

## 実施内容 / Implementation

## 検証結果 / Validation Results

## 影響範囲と今後の課題 / Impact and Future Issues

## 実施内容

## 検証結果

## 成果物 (Deliverables)
- `github_broker/application/task_service.py`

## 影響範囲と今後の課題

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-design-doc-001`
- **作業ブランチ (Feature Branch):** `story/implement-review-issue-handling`
