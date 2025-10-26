# 【Task】`TaskService` から `review_comments` の取得・保存ロジックを削除する

## 目的とゴール / Purpose and Goals
このTaskの目的は、`TaskService` から `review_comments` の取得および保存に関するロジックを削除することです。

## 実施内容 / Implementation
- `github_broker/application/task_service.py` を開き、`get_review_comments` の呼び出しと `review_comments` の保存処理を削除します。
- 関連するテストコードを修正します。

## 検証結果 / Validation Results
- `TaskService` から関連ロジックが削除され、テストが成功すること。

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
- `TaskService` が `get_review_comments` を呼び出し、結果を `review_comments` としてRedisに保存している。

## To-be (あるべき姿)
- `TaskService` から `get_review_comments` の呼び出しと、`review_comments` の保存処理が削除されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py` を開く。
2. `get_review_comments` を呼び出している箇所を削除する。
3. Redisに `review_comments` を保存している箇所を削除する。
4. 関連するテストコードを修正する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。

## 成果物 (Deliverables)
- 更新された `github_broker/application/task_service.py`
- 更新された `tests/application/test_task_service.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/remove-review-comments-variable`
- **作業ブランチ (Feature Branch):** `task/modify-task-service-for-review-comments`