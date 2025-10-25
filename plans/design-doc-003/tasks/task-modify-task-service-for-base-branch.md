# 【Task】`TaskService` が `base_branch_name` を取得・保存するように変更する

## 目的とゴール / Purpose and Goals
このTaskの目的は、`TaskService` がIssueのペイロードからベースブランチ名を取得し、Redisに保存するように変更することです。

## 実施内容 / Implementation
- `github_broker/application/task_service.py` を開き、Issue情報取得処理で `base.ref` の値を取得し、`base_branch_name` としてRedisに保存するロジックを追加します。
- 関連するテストコードを修正します。

## 検証結果 / Validation Results
- `TaskService` が `base_branch_name` を正しく取得・保存し、テストが成功すること。

## 影響範囲と今後の課題 / Impact and Future Issues
- 影響範囲: `TaskService` のロジック。
- 今後の課題: なし。

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `docs/design-docs/003-prompt-template-updates.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- `TaskService` がIssueのペイロードからベースブランチ名を取得していない。

## To-be (あるべき姿)
- `TaskService` がIssueのペイロードからベースブランチ名（`base.ref`）を取得し、Redisに `base_branch_name` として保存する。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py` を開く。
2. Issue情報取得処理で、`base.ref` の値を取得するロジックを追加する。
3. 取得した値を `base_branch_name` としてRedisに保存するロジックを追加する。
4. 関連するテストコードを修正する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。

## 成果物 (Deliverables)
- 更新された `github_broker/application/task_service.py`
- 更新された `tests/application/test_task_service.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/add-base-branch-name-variable`
- **作業ブランチ (Feature Branch):** `task/modify-task-service-for-base-branch`