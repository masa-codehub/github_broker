
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
親Epic「ローカルリファクタリングと集約」の最初のステップとして、移行先となる`issue_creator_kit`パッケージの骨格を`github_broker`リポジトリ内に準備します。現状分析として、移行対象のコードを受け入れるための明確に定義されたディレクトリ構造や、Pythonパッケージとして管理するための`pyproject.toml`が存在しないため、機能移行に着手できない状態です。

## To-be (あるべき姿)
As-isの問題を解決するため、ADR-018で定義されたClean Architectureに基づくディレクトリ構造と、基本的なパッケージ情報を定義した`pyproject.toml`を作成します。これにより、後続の機能移行Story（ドキュメント検証、Issue作成）がスムーズに着手できるための、明確で安定した基盤（=受け皿）が構築された状態になります。

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
