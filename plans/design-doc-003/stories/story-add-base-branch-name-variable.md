# 【Story】`{base_branch_name}` 変数と関連処理の追加

## 目的とゴール / Purpose and Goals
このStoryの目的は、プロンプトで `{base_branch_name}` 変数を利用可能にするため、関連するデータ取得、保存、置換のロジックをコードベースに追加することです。

## 実施内容 / Implementation
- `task-modify-task-service-for-base-branch`: `TaskService` を修正します。
- `task-modify-redis-schema-for-base-branch`: Redisスキーマを更新します。
- `task-modify-gemini-executor-for-base-branch`: `GeminiExecutor` を修正します。

## 検証結果 / Validation Results
- `base_branch_name` がプロンプトに正しく置換され、テストが成功すること。

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
- `TaskService` がベースブランチ名を取得・保存していない。
- Redisに `base_branch_name` が存在しない。
- `GeminiExecutor` がプロンプトで `{base_branch_name}` を使用していない。

## To-be (あるべき姿)
- `TaskService` がIssueのペイロードからベースブランチ名を取得し、Redisに `base_branch_name` として保存する。
- `GeminiExecutor` がRedisから `base_branch_name` を読み込み、プロンプトテンプレートの変数を置換する。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `task-modify-task-service-for-base-branch` を行い、`TaskService` を修正する。
2. `task-modify-redis-schema-for-base-branch` を行い、Redisスキーマを更新する。
3. `task-modify-gemini-executor-for-base-branch` を行い、`GeminiExecutor` を修正する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。

## 成果物 (Deliverables)
- 更新された `github_broker/application/task_service.py`
- 更新された `github_broker/infrastructure/gemini_executor.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-design-doc-003`
- **作業ブランチ (Feature Branch):** `story/add-base-branch-name-variable`