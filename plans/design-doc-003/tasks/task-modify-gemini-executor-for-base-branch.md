# 【Task】`GeminiExecutor` が `base_branch_name` を読み込み、プロンプトを置換するように変更する

## 目的とゴール / Purpose and Goals
このTaskの目的は、`GeminiExecutor` がRedisから `base_branch_name` を読み込み、プロンプトの `{base_branch_name}` 変数を置換するように変更することです。

## 実施内容 / Implementation
- `github_broker/infrastructure/executors/gemini_executor.py` を開き、Redisから `base_branch_name` を取得し、プロンプトの `{base_branch_name}` 変数を置換するロジックを追加します。
- 関連するテストコードを修正します。

## 検証結果 / Validation Results
- `GeminiExecutor` が `base_branch_name` を正しく置換し、テストが成功すること。

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
- `GeminiExecutor` がRedisから `base_branch_name` を読み込んでいない。

## To-be (あるべき姿)
- `GeminiExecutor` がRedisから `base_branch_name` を読み込み、プロンプトの `{base_branch_name}` 変数を置換する。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/infrastructure/executors/gemini_executor.py` を開く。
2. Redisから `base_branch_name` を取得するロジックを追加する。
3. プロンプトの `{base_branch_name}` 変数を置換するロジックを追加する。
4. 関連するテストコードを修正する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。

## 成果物 (Deliverables)
- 更新された `github_broker/infrastructure/executors/gemini_executor.py`
- 更新された `tests/infrastructure/executors/test_gemini_executor.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/add-base-branch-name-variable`
- **作業ブランチ (Feature Branch):** `task/modify-gemini-executor-for-base-branch`