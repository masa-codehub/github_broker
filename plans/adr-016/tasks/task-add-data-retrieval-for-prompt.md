# 【Task】プロンプト生成に必要な情報取得ロジックの追加

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/016-fix-review-issue-assignment-logic.md`

## As-is (現状)
`_find_first_assignable_task` メソッド内で、レビュー修正タスク用のプロンプトに必要な `pr_url` と `review_comments` を取得するロジックが存在しない。

## To-be (あるべき姿)
`_find_first_assignable_task` メソッド内で、タスクが `TaskType.REVIEW` の場合、`github_client` を使って `pr_url` と `review_comments` を取得するロジックが実装されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py` の `_find_first_assignable_task` メソッドを修正する。
2. `task.task_type == TaskType.REVIEW` の条件分岐を追加する。
3. `self.github_client.get_pr_for_issue(task.issue_id)` を呼び出して `pr_url` を取得する。
4. `self.github_client.get_pull_request_review_comments(pr_number)` を呼び出して `review_comments` を取得する。
5. 単体テストを作成し、修正が正しく動作することを確認する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` の修正

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/fix-review-issue-workflow`
- **作業ブランチ (Feature Branch):** `task/add-data-retrieval-for-prompt`
