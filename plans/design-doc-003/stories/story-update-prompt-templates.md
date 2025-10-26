# 【Story】プロンプトテンプレートの更新

## 目的とゴール / Purpose and Goals
このStoryの目的は、`github_broker/infrastructure/prompts/gemini_executor.yml` に定義されているプロンプトテンプレートを、デザインドキュメントの指示に従って更新することです。

## 実施内容 / Implementation
- `task-update-gemini-executor-yml`: `gemini_executor.yml` ファイルを更新します。

## 検証結果 / Validation Results
- `gemini_executor.yml` が正しく更新され、テストが成功すること。

## 影響範囲と今後の課題 / Impact and Future Issues
- 影響範囲: プロンプト生成ロジック。
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
- `github_broker/infrastructure/prompts/gemini_executor.yml` に定義されているプロンプトテンプレートが古い。

## To-be (あるべき姿)
- `github_broker/infrastructure/prompts/gemini_executor.yml` の `prompt_template` と `review_fix_prompt_template` が、デザインドキュメントで定義された最終FIX版に更新されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `task-update-gemini-executor-yml` を行い、`gemini_executor.yml` ファイルを更新する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。

## 成果物 (Deliverables)
- 更新された `github_broker/infrastructure/prompts/gemini_executor.yml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-design-doc-003`
- **作業ブランチ (Feature Branch):** `story/update-prompt-templates`