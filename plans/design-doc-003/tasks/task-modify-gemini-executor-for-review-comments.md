# 【Task】`GeminiExecutor` から `review_comments` の置換ロジックを削除する

## 目的とゴール / Purpose and Goals
このTaskの目的は、`GeminiExecutor` から `review_comments` の読み込みとプロンプト置換に関するロジックを削除することです。

## 実施内容 / Implementation
- `github_broker/infrastructure/executors/gemini_executor.py` を開き、`review_comments` の取得と置換処理を削除します。
- 関連するテストコードを修正します。

## 検証結果 / Validation Results
- `GeminiExecutor` から関連ロジックが削除され、テストが成功すること。

## 影響範囲と今後の課題 / Impact and Future Issues
- 影響範囲: `GeminiExecutor` のプロンプト生成ロジック。
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
- `GeminiExecutor` がRedisから `review_comments` を読み込み、プロンプトの `{review_comments}` 変数を置換している。

## To-be (あるべき姿)
- `GeminiExecutor` から `review_comments` の読み込みと置換処理が削除されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/infrastructure/executors/gemini_executor.py` を開く。
2. Redisから `review_comments` を取得している箇所を削除する。
3. プロンプトの `{review_comments}` 変数を置換している箇所を削除する。
4. 関連するテストコードを修正する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。

## 成果物 (Deliverables)
- 更新された `github_broker/infrastructure/executors/gemini_executor.py`
- 更新された `tests/infrastructure/executors/test_gemini_executor.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/remove-review-comments-variable`
- **作業ブランチ (Feature Branch):** `task/modify-gemini-executor-for-review-comments`