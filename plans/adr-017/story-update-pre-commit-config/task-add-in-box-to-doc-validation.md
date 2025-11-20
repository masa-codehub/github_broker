# 【Task】doc-validationの対象パス追加

## 親Issue (Parent Issue)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/017-commit-triggered-issue-creation.md`

## 実装の参照資料 (Implementation Reference Documents)
- `docs/architecture/adr--017-issue-creator-workflow/index.md`

## As-is (現状)
`.pre-commit-config.yaml`ファイルに定義されている`doc-validation`フックの`files`キーは、`/_in_box/`ディレクトリ内のファイルを対象とするパターンを含んでいない。

## To-be (あるべき姿)
ADR-017の`決定`事項に基づき、`.pre-commit-config.yaml`の`doc-validation`フックが更新され、`files`の正規表現パターンに`/_in_box/`内のMarkdownファイル（`_in_box/.*\.md$`）が追加されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `.pre-commit-config.yaml`の`doc-validation`フックにおける`files`キーの値を編集し、既存の正規表現パターンに`_in_box/.*\.md$`を追加する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- `.pre-commit-config.yaml`の`doc-validation`フックが`/_in_box/`内のMarkdownファイルを正しく検証すること。

## 成果物 (Deliverables)
- `.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/update-pre-commit-config`
- **作業ブランチ (Feature Branch):** `task/add-in-box-to-doc-validation`
