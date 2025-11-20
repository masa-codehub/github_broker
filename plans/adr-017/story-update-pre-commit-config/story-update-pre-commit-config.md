# 【Story】pre-commitフック設定の更新

## 親Issue (Parent Issue)
- (起票後に追記)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/017-commit-triggered-issue-creation.md`

## 実装の参照資料 (Implementation Reference Documents)
- `docs/architecture/adr-017-issue-creator-workflow/index.md`

## As-is (現状)
`.pre-commit-config.yaml`ファイルに定義されている既存の`pre-commit`フック（`doc-validation`）は、`/_in_box/`フォルダ内のファイルを検証対象としていない。

## To-be (あるべき姿)
ADR-017の`決定`事項に基づき、`.pre-commit-config.yaml`の`doc-validation`フックの設定が更新され、`/_in_box/`フォルダ内に存在するMarkdownファイル（`*.md`）が、Pull Requestの時点でフォーマットの妥当性を確実にチェックされるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `.pre-commit-config.yaml`ファイルを開き、`id: doc-validation`を持つフックの`files`キーに、`/_in_box/`内のMarkdownファイルを対象とする正規表現パターン（例: `_in_box/.*\.md$`）を追加する (`Task: A`)

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `/_in_box`フォルダ内に不正なフォーマットのIssueファイルを追加したPull Requestで、CIの`doc-validation`チェックが失敗すること。

## 成果物 (Deliverables)
- 更新された`.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-017`
- **作業ブランチ (Feature Branch):** `story/update-pre-commit-config`
