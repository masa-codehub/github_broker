# 【Task】プロンプト切り替えロジックの追加

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/016-fix-review-issue-assignment-logic.md`

## As-is (現状)
`_find_first_assignable_task` メソッドは、タスクの種類に関わらず常に開発用のプロンプト (`gemini_executor.build_prompt`) を生成している。

## To-be (あるべき姿)
`_find_first_assignable_task` メソッドがタスクの種類を判別し、`TaskType.DEVELOPMENT` の場合は `gemini_executor.build_prompt` を、`TaskType.REVIEW` の場合は `gemini_executor.build_code_review_prompt` を呼び出してプロンプTを生成するようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py` の `_find_first_assignable_task` メソッドを修正する。
2. `task.task_type` の値に応じて、呼び出す `gemini_executor` のメソッドを切り替えるロジックを実装する。
3. `TaskType.REVIEW` の場合は、前Taskで取得した `pr_url` と `review_comments` を `build_code_review_prompt` に渡す。
4. 単体テストを作成し、修正が正しく動作することを確認する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体Testが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` の修正

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/fix-review-issue-workflow`
- **作業ブランチ (Feature Branch):** `task/add-prompt-switching-logic`
