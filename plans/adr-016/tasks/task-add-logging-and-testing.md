# 【Task】動作検証のためのログ追加とテストコード修正
# Issue: #1821

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/016-fix-review-issue-assignment-logic.md`

## As-is (現状)
プロンプト切り替えに関するログがなく、テストも不十分である。

## To-be (あるべき姿)
`_find_first_assignable_task` メソッドで、どちらのプロンプト生成メソッドが呼び出されたかを示すログが出力される。また、`test_task_service.py` に、レビュー修正タスクの割り当てとプロンプト生成を検証するテストケースが追加されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py` の `_find_first_assignable_task` メソッドに、プロンプト生成メソッドの呼び出しに関するINFOレベルのログを追加する。
2. `tests/application/test_task_service.py` を開き、`needs-review` ラベルを持つIssueをモックデータとして準備する。
3. レビュー修正タスクが正しく割り当てられ、`gemini_executor.build_code_review_prompt` が適切な引数で呼び出されることを検証するテストケースを追加する。
4. 開発タスクの場合に `gemini_executor.build_prompt` が呼び出されるテストケースも確認・修正する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- Brokerのログで、タスクの種類に応じたプロンプト生成メソッドの呼び出しが確認できること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` の修正
- `tests/application/test_task_service.py` の修正・追加

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/fix-review-issue-workflow`
- **作業ブランチ (Feature Branch):** `task/add-logging-and-testing`
