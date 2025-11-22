
# 【Task】pyproject.tomlを作成し、パッケージ情報とCLIエントリーポイントを定義する

## 親Issue (Parent Issue)
- `_in_box/adr-018/epic-phase1-local-refactoring/story-build-foundation/story-build-foundation.md`

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## As-is (現状)
親Story「issue_creator_kitの基盤を構築する」に基づき、`issue_creator_kit`をインストール可能なPythonパッケージとして定義します。現状では、パッケージのメタデータ、依存関係、そして`doc-validator`や`issue-creator`といった重要なCLIエントリーポイントを定義するための`pyproject.toml`ファイルが存在していません。

## To-be (あるべき姿)
As-isの要求に基づき、`pyproject.toml`ファイルが作成され、基本的なパッケージ定義とCLIエントリーポイントが記述されます。これにより、`pip install -e .`コマンドでの編集可能モードでのインストールが可能になり、後続の「参照更新と検証」Storyの前提条件が整った状態になります。

## 完了条件 (Acceptance Criteria)
- TDDのサイクルに従って実装と単体テストが完了していること（このTaskでは主に設定ファイル作成なので、内容の正しさが検証できればよい）。
- `issue_creator_kit/pyproject.toml`が作成されていること。
- `[project]`テーブルにパッケージ名、バージョンなどの基本情報が定義されていること。
- `[project.scripts]`テーブルに`doc-validator`と`issue-creator`のエントリーポイントが正しく定義されていること。

## 成果物 (Deliverables)
- `issue_creator_kit/pyproject.toml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/build-ick-foundation`
- **作業ブランチ (Feature Branch):** `task/create-pyproject-toml`
