# 【Story】`{review_comments}` 変数と関連処理の削除

## 目的とゴール / Purpose and Goals
このStoryの目的は、プロンプトから `{review_comments}` 変数を削除し、関連するデータ取得、保存、置換のロジックをコードベースから完全に削除することです。

## 実施内容 / Implementation
- `task-modify-task-service-for-review-comments`: `TaskService` を修正します。
- `task-modify-redis-schema-for-review-comments`: Redisスキーマを更新します。
- `task-modify-gemini-executor-for-review-comments`: `GeminiExecutor` を修正します。

## 検証結果 / Validation Results
- `review_comments` に関連する処理が削除され、テストが成功すること。

## 影響範囲と今後の課題 / Impact and Future Issues
- 影響範囲: `TaskService`, `GeminiExecutor`, Redisスキーマ。
- 今後の課題: なし。

## 親Issue (Parent Issue)
- (Epic起票後に追記)

## 子Issue (Sub-Issues)
- (Task起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/design-docs/003-prompt-template-updates.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- `TaskService` がレビューコメントを取得し、Redisに `review_comments` として保存している。
- `GeminiExecutor` がプロンプトの `{review_comments}` 変数を置換している。

## To-be (あるべき姿)
- `TaskService` から `review_comments` の取得・保存ロジックが削除されている。
- Redisのスキーマから `review_comments` フィールドが削除されている。
- `GeminiExecutor` から `{review_comments}` 変数の置換ロジックが削除されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `task-modify-task-service-for-review-comments` を行い、`TaskService` を修正する。
2. `task-modify-redis-schema-for-review-comments` を行い、Redisスキーマを更新する。
3. `task-modify-gemini-executor-for-review-comments` を行い、`GeminiExecutor` を修正する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。

## 成果物 (Deliverables)
- 更新された `github_broker/application/task_service.py`
- 更新された `github_broker/infrastructure/executors/gemini_executor.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-design-doc-003`
- **作業ブランチ (Feature Branch):** `story/remove-review-comments-variable`