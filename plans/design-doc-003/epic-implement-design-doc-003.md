# 【Epic】プロンプトテンプレートの更新と関連アーキテクチャの変更

## 目的とゴール / Purpose and Goals
このEpicの目的は、`docs/design-docs/003-prompt-template-updates.md` に基づき、AIエージェントのプロンプトテンプレートを更新し、関連するアーキテクチャを修正することです。これにより、エージェントのタスク実行の信頼性と一貫性を向上させます。

## 実施内容 / Implementation
- `story-update-prompt-templates`: プロンプトテンプレートを更新します。
- `story-remove-review-comments-variable`: `{review_comments}` 変数と関連処理を削除します。
- `story-add-base-branch-name-variable`: `{base_branch_name}` 変数と関連処理を追加します。

## 検証結果 / Validation Results
- すべての子Storyが完了し、統合テストが成功すること。

## 影響範囲と今後の課題 / Impact and Future Issues
- 影響範囲: `github_broker` のプロンプト生成、タスク管理、Redisスキーマ。
- 今後の課題: なし。

## 親Issue (Parent Issue)
- (なし)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/design-docs/003-prompt-template-updates.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- プロンプトテンプレートが古く、エージェントへの指示が曖昧。
- レビューコメントがRedisに保存されている。
- ベースブランチ名がプロンプトに渡されていない。

## To-be (あるべき姿)
- プロンプトテンプレートが更新され、エージェントへの指示が明確になる。
- レビューコメントの取得がエージェントの責務となり、Redisから関連フィールドが削除される。
- ベースブランチ名がプロンプトに渡され、エージェントが常に最新のコードベースで作業できる。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `story-update-prompt-templates` を行い、プロンプトテンプレートを更新する。
2. `story-remove-review-comments-variable` を行い、レビューコメント関連の処理を削除する。
3. `story-add-base-branch-name-variable` を行い、ベースブランチ名関連の処理を追加する。

## 完了条件 (Acceptance Criteria)
- このEpicを構成する全てのStoryの実装が完了していること。
- 各Storyの成果物を組み合わせた統合テストが成功し、関連する意思決定ドキュメント（ADR/Design Doc）の要求事項をすべて満たしていることが確認されること。

## 成果物 (Deliverables)
- 更新された `github_broker/infrastructure/prompts/gemini_executor.yml`
- 更新された `github_broker/application/task_service.py`
- 更新された `github_broker/infrastructure/executors/gemini_executor.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-design-doc-003`