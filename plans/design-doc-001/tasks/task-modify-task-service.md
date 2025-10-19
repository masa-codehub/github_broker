# Issue: #1527
Status: Open
# 【Task】`TaskService`を修正し、レビューIssueの検索クエリを更新し、遅延処理を実装する

## 親Issue (Parent Issue)
- #1523

## 子Issue (Sub-Issues)
- (なし)

## As-is (現状)
`TaskService`のレビューIssue検索ロジックが古く、遅延処理が存在しない。

## To-be (あるべき姿)
`TaskService`のレビューIssue検索クエリが`is:issue label:needs-review linked:pr is:open`に更新され、Redisを利用した5分間の遅延割り当て処理が実装される。

## 完了条件 (Acceptance Criteria)
- `TaskService`に、GitHub検索クエリ`is:issue label:needs-review linked:pr is:open`を使用する新しいメソッド `_find_review_task` が作成されていること。
  - **Note:** このタスクは、`github_client`に`get_open_issues`とは別に、上記のクエリでIssueを取得するための新しいメソッド `get_review_issues` が実装されていることを前提とします。
- `start_polling`メソッド内で`_find_review_task`が呼び出され、検出したIssueの`issue_id`と現在時刻のタイムスタンプがRedisに保存されること。（キー例: `review_issue_detected_timestamp:{issue_id}`）
- `request_task`メソッド呼び出し時に、`needs-review`ラベルを持つIssueが候補となった場合、Redisに保存されたタイムスタンプを確認し、5分以上経過したIssueのみをタスクとして返却するロジックが追加されていること。
- 関連する単体テストがすべてパスすること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/implement-review-issue-handling`
- **作業ブランチ (Feature Branch):** `task/modify-task-service`
