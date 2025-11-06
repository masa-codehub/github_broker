# 【Task】`gemini_executor.yml` のプロンプトテンプレートを更新する

## 目的とゴール / Purpose and Goals
このTaskの目的は、`github_broker/infrastructure/prompts/gemini_executor.yml` ファイル内の `prompt_template` と `review_fix_prompt_template` を、デザインドキュメントで指定された内容に更新することです。

## 実施内容 / Implementation
- `github_broker/infrastructure/prompts/gemini_executor.yml` を開き、`prompt_template` と `review_fix_prompt_template` をデザインドキュメントの最終FIX版に書き換えます。

## 検証結果 / Validation Results
- ファイルが正しく更新され、関連するテストが成功すること。

## 影響範囲と今後の課題 / Impact and Future Issues
- 影響範囲: エージェントが使用するプロンプト。
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
- `github_broker/infrastructure/prompts/gemini_executor.yml` のプロンプトテンプレートが古い。

## To-be (あるべき姿)
- `github_broker/infrastructure/prompts/gemini_executor.yml` の `prompt_template` と `review_fix_prompt_template` が、デザインドキュメントで定義された最終FIX版に更新されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/infrastructure/prompts/gemini_executor.yml` を開く。
2. `prompt_template` をデザインドキュメントの最終FIX版に書き換える。
3. `review_fix_prompt_template` をデザインドキュメントの最終FIX版に書き換える。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。

## 成果物 (Deliverables)
- 更新された `github_broker/infrastructure/prompts/gemini_executor.yml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/update-prompt-templates`
- **作業ブランチ (Feature Branch):** `task/update-gemini-executor-yml`