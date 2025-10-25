# 【Story】`{base_branch_name}` 変数と関連処理の追加

## 目的とゴール / Purpose and Goals
このStoryの目的は、プロンプトで `{base_branch_name}` 変数を利用可能にするため、責務分離の原則に従って、関連するデータ取得、保存、引き渡しのロジックをコードベースに追加することです。

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
- `TaskService` がタスクの種類に応じて `base_branch_name` を特定し、Redisに保存する。
- `GeminiExecutor` のプロンプト構築メソッドが、`TaskService` から `base_branch_name` を引数として受け取り、プロンプトテンプレートの変数を置換する。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `task-modify-redis-schema-for-base-branch` を行い、Redisスキーマとドメインモデルを更新する。
2. `task-modify-gemini-executor-for-base-branch` を行い、`GeminiExecutor` のメソッドシグネチャを修正する。
3. `task-modify-task-service-for-base-branch` を行い、`TaskService` に `base_branch_name` の特定、保存、および `GeminiExecutor` への引き渡しロジックを追加する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。

## 成果物 (Deliverables)
- 更新された `github_broker/application/task_service.py`
- 更新された `github_broker/infrastructure/executors/gemini_executor.py`
- 更新された `github_broker/domain/task.py`
- 更新された `docs/architecture/redis-schema.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-design-doc-003`
- **作業ブランチ (Feature Branch):** `story/add-base-branch-name-variable`
