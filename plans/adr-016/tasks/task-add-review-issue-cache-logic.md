# 【Task】レビュー修正タスクのキャッシュ処理追加
# Issue: #1818

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/016-fix-review-issue-assignment-logic.md`

## As-is (現状)
`_find_review_task` メソッドで取得したレビューIssueがRedisにキャッシュされていない。

## To-be (あるべき姿)
`_find_review_task` メソッド内で `get_review_issues` を呼び出した後、取得したIssueリストが `redis_client.sync_issues` を使ってRedisにキャッシュされる。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py` の `_find_review_task` メソッドを修正する。
2. `self.github_client.get_review_issues()` の呼び出しの直後に `self.redis_client.sync_issues(review_issues)` を追加する。
3. 単体テストを作成し、修正が正しく動作することを確認する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- `redis-cli` で `issue:*` キーを確認し、`needs-review` ラベルを持つIssueがキャッシュされていること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` の修正

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/fix-review-issue-workflow`
- **作業ブランチ (Feature Branch):** `task/add-review-issue-cache-logic`
