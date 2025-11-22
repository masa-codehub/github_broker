
# 【Story】不要なファイルをクリーンアップする

## 親Issue (Parent Issue)
- `_in_box/adr-018/epic-phase1-local-refactoring.md`

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- `issue_creator_kit`への機能移行後も、`github_broker`リポジトリ内に古いソースコードとテストが残っている可能性がある。

## To-be (あるべき姿)
- `github_broker/infrastructure/document_validation/`, `github_broker/infrastructure/github_actions/`, `tests/infrastructure/document_validation/`, `tests/infrastructure/github_actions/` が完全に削除されている。
- ADR-017関連のドキュメントで、実装が`issue_creator_kit`に分離された旨が追記されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `git rm -r` コマンドを使用して、指定された古いディレクトリをすべて削除する。
2. `docs/adr/017-commit-triggered-issue-creation.md` を編集し、実装の現状について追記する。
3. すべてのテストが引き続きパスすることを確認する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- 指定されたディレクトリが`github_broker`リポジトリから完全に削除されていること。
- ADR-017のドキュメントが更新されていること。

## 成果物 (Deliverables)
- 更新された `docs/adr/017-commit-triggered-issue-creation.md`
- 削除されたディレクトリの証明（`git log`など）

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/adr018-phase1-refactoring`
- **作業ブランチ (Feature Branch):** `story/cleanup-old-files`
