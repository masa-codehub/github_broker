---
title: "【Task】検証CLIの作成"
labels:
  - "task"
  - "adr-019"
  - "P2"
  - "BACKENDCODER"
---
# 【Task】検証CLIの作成

## 親Issue (Parent Issue)
- `story-integrate-pre-commit-hook` (起票後にIssue番号を記載)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/019-fix-issue-creator-workflow.md`

## As-is (現状)
`ValidationService`を呼び出すためのCLIエントリーポイントが存在しない。

## To-be (あるべき姿)
`issue_creator_kit/interface/validation_cli.py`に、コマンドラインからファイルパスを引数として受け取り、`ValidationService`の`validate_frontmatter`関数を呼び出すCLIが実装されている。検証が成功した場合は終了コード0を、失敗した場合はエラーメッセージを標準エラー出力に出力し、終了コード1を返す。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `issue_creator_kit/interface/validation_cli.py`ファイルを作成する。
2. `argparse`や`click`などを用いて、ファイルパスを引数として受け取るCLIを実装する。
3. `ValidationService`をインスタンス化し、`validate_frontmatter`を呼び出す。
4. `try...except`ブロックを使用して、`ValidationService`から送出される例外を捕捉し、標準エラーにメッセージを出力して終了コード1で終了する処理を実装する。
5. 検証が成功した場合は、終了コード0で正常終了する。

## 完了条件 (Acceptance Criteria)
- 作成したCLIに対して、有効なファイルパスを渡すと終了コード0で終了すること。
- 無効なファイルパスを渡すと、エラーメッセージを出力し、終了コード1で終了すること。

## 成果物 (Deliverables)
- `issue_creator_kit/interface/validation_cli.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/integrate-pre-commit-hook`
- **作業ブランチ (Feature Branch):** `task/create-validation-cli`
