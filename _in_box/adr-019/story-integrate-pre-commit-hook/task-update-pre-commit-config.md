---
title: "【Task】pre-commit設定の更新"
labels:
  - "task"
  - "adr-019"
  - "P3"
  - "BACKENDCODER"
---
# 【Task】pre-commit設定の更新

## 親Issue (Parent Issue)
- `story-integrate-pre-commit-hook` (起票後にIssue番号を記載)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/019-fix-issue-creator-workflow.md`

## As-is (現状)
`.pre-commit-config.yaml`には、`_in_box`配下のMarkdownファイルのフロントマターを検証するフックが設定されていない。

## To-be (あるべき姿)
`.pre-commit-config.yaml`に定義されている既存の`doc-validation-in-box`フック（`doc-validator`コマンド）が、`_in_box/`配下のMarkdownファイルに対して、ADR-019で定義されたフロントマターの検証も行うように拡張されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `.pre-commit-config.yaml`を開き、既存の`doc-validation-in-box`フックが`issue_creator_kit.interface.validation_cli:main`を指していることを再確認する。
2. `issue_creator_kit.interface.validation_cli.py`の`main`関数に、フロントマターを検証する`ValidationService`のロジックを追加・統合する。
3. `pre-commit run doc-validation-in-box --all-files`などを実行し、フックがフロントマター検証を正しく実行することを確認する。

## 完了条件 (Acceptance Criteria)
- `.pre-commit-config.yaml`が更新され、新しいフックが正しく定義されていること。
- 不正なファイルを持つ`_in_box`内のファイルに対してコミットを試みると、`Issue Frontmatter Validator`フックが失敗し、コミットが中断されること。

## 成果物 (Deliverables)
- `.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/integrate-pre-commit-hook`
- **作業ブランチ (Feature Branch):** `task/update-pre-commit-config`
