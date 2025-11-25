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
`.pre-commit-config.yaml`に新しい`id: issue-frontmatter-validator`が追加されている。このフックは`_in_box/`配下の`*.md`ファイルを対象とし、`entry`として`python -m issue_creator_kit.interface.validation_cli`（または`pyproject.toml`で設定したエントリーポイント）を呼び出すように設定されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `.pre-commit-config.yaml`を開く。
2. 既存の`doc-validator`フックを参考に、新しいフック定義を追加する。
   - `id`: `issue-frontmatter-validator`
   - `name`: `Issue Frontmatter Validator`
   - `entry`: （`task/create-validation-cli`で実装したCLIを呼び出すコマンド）
   - `language`: `python`
   - `types`: `[markdown]`
   - `files`: `^_in_box/.*\.md$`
3. 設定後、`pre-commit run issue-frontmatter-validator --all-files`などを実行し、フックが正しく動作することを確認する。

## 完了条件 (Acceptance Criteria)
- `.pre-commit-config.yaml`が更新され、新しいフックが正しく定義されていること。
- 不正なファイルを持つ`_in_box`内のファイルに対してコミットを試みると、`Issue Frontmatter Validator`フックが失敗し、コミットが中断されること。

## 成果物 (Deliverables)
- `.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/integrate-pre-commit-hook`
- **作業ブランチ (Feature Branch):** `task/update-pre-commit-config`
