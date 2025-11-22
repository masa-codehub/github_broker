
# 【Story】issue_creator_kitの基盤を構築する

## 親Issue (Parent Issue)
- `_in_box/adr-018/epic-phase1-local-refactoring.md`

## 子Issue (Sub-Issues)
- `_in_box/adr-018/epic-phase1-local-refactoring/story-build-foundation/task-create-directory-structure.md`
- `_in_box/adr-018/epic-phase1-local-refactoring/story-build-foundation/task-create-pyproject-toml.md`

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- `github_broker`リポジトリ内に`issue_creator_kit`のディレクトリが存在しない。

## To-be (あるべき姿)
- `github_broker`リポジトリのルートに、ADR-018で定義されたClean Architectureに基づく`issue_creator_kit`のディレクトリ構造が作成されている。
- `issue_creator_kit`をPythonパッケージとして定義する`pyproject.toml`が作成されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: issue_creator_kitのディレクトリ構造を作成する` を実行する。
2. `Task: pyproject.tomlを作成し、パッケージ情報とCLIエントリーポイントを定義する` を実行する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `issue_creator_kit`ディレクトリと、その配下の`issue_creator_kit`, `tests`などのサブディレクトリが作成されていること。
- `issue_creator_kit/pyproject.toml`が作成され、基本的なパッケージ情報と`doc-validator`, `issue-creator`のスクリプトエントリーポイントが定義されていること。

## 成果物 (Deliverables)
- `issue_creator_kit/` ディレクトリ構造
- `issue_creator_kit/pyproject.toml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/adr018-phase1-refactoring`
- **作業ブランチ (Feature Branch):** `story/build-ick-foundation`
