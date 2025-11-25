---
title: "【Task】検証CLIの作成"
labels:
  - "task"
  - "adr-019"
  - "P2"
  - "BACKENDCODER"
---
# 【Task】既存の検証CLIへの機能追加

## 親Issue (Parent Issue)
- `story-integrate-pre-commit-hook` (起票後にIssue番号を記載)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/019-fix-issue-creator-workflow.md`

## As-is (現状)
`issue_creator_kit.interface.validation_cli:main`は存在するが、ADR-019で要求されるフロントマターの検証機能は実装されていない。

## To-be (あるべき姿)
`issue_creator_kit.interface.validation_cli.py`が修正され、既存の検証ロジックに加えて、`ValidationService`の`validate_frontmatter`関数を呼び出す処理が追加されている。検証が失敗した場合は、従来通り終了コード1で終了する。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `issue_creator_kit/interface/validation_cli.py`を開く。
2. `main`関数内に、`ValidationService`を呼び出してフロントマターを検証するロジックを追加する。
3. `try...except`ブロックを適切に設定し、既存の検証と新しい検証のいずれかが失敗した場合でも、終了コード1で終了するようにする。

## 完了条件 (Acceptance Criteria)
- 作成したCLIに対して、有効なファイルパスを渡すと終了コード0で終了すること。
- 無効なファイルパスを渡すと、エラーメッセージを出力し、終了コード1で終了すること。

## 成果物 (Deliverables)
- `issue_creator_kit/interface/validation_cli.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/integrate-pre-commit-hook`
- **作業ブランチ (Feature Branch):** `task/create-validation-cli`
