---
title: "【Story】検証ロジックのpre-commitフックへの統合"
labels:
  - "story"
  - "adr-019"
  - "P3"
  - "PRODUCT_MANAGER"
---
# 【Story】検証ロジックのpre-commitフックへの統合

## 親Issue (Parent Issue)
- `epic-implement-adr-019` (起票後にIssue番号を記載)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/019-fix-issue-creator-workflow.md`

## As-is (現状)
`pre-commit`フックには、`_in_box`配下のMarkdownファイルのフロントマターを検証する仕組みがない。

## To-be (あるべき姿)
`ValidationService`を呼び出すCLIが実装され、`.pre-commit-config.yaml`に登録される。これにより、`_in_box`配下のファイルに対するコミット時に、ADR-019で定義された検証が自動的に実行される状態になる。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `ValidationService`を呼び出し、結果に応じて終了コードを返すCLIを作成する (`Task: Create Validation CLI`)。
2. `.pre-commit-config.yaml`を更新し、新しいCLIを`_in_box`配下のファイルに適用するフックを追加する (`Task: Update Pre-commit Config`)。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- 不正なフロントマターを持つファイルを`_in_box`にコミットしようとすると、pre-commitフックが失敗すること。
- 正常なフロントマターを持つファイルは、問題なくコミットできること。

## 成果物 (Deliverables)
- `issue_creator_kit/interface/validation_cli.py`
- `.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-019-validation`
- **作業ブランチ (Feature Branch):** `story/integrate-pre-commit-hook`
