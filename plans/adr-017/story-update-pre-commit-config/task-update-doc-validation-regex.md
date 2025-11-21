# 【Task】doc-validationフックの正規表現を更新

## 親Issue (Parent Issue)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/017-commit-triggered-issue-creation.md`

## 実装の参照資料 (Implementation Reference Documents)
- `docs/architecture/adr-017-issue-creator-workflow/index.md`

## As-is (現状)
`.pre-commit-config.yaml`の`doc-validation`フックの`files`キーに設定された正規表現が、以下の2つの問題を抱えている。
1. `/_in_box/`ディレクトリ内のファイルを検証対象としていない。
2. `plans/`ディレクトリのサブディレクトリ内のファイルを検証対象から漏らしている。

## To-be (あるべき姿)
`doc-validation`フックの`files`キーの正規表現が修正され、`/_in_box/`ディレクトリと`plans/`配下のすべてのサブディレクトリ内のMarkdownファイルが、`pre-commit`の検証対象に正しく含まれている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `.pre-commit-config.yaml`の`doc-validation`フックにおける`files`キーの値を、`^(docs/adr/|docs/design-docs/|plans/.*|_in_box/).*\.md$` という正規表現に修正する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- `plans/`配下のサブディレクトリ、および`_in_box/`ディレクトリに検証対象ファイルを追加したコミット時に、`doc-validation`フックが正しく実行されること。

## 成果物 (Deliverables)
- `.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/update-pre-commit-config`
- **作業ブランチ (Feature Branch):** `task/update-doc-validation-regex`

## 子Issue (Sub-Issues)

- 
