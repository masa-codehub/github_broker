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
`.pre-commit-config.yaml`ファイルに定義されている`doc-validation`フックが、`/_in_box/`フォルダ内のファイルを検証対象としておらず、また`plans/`ディレクトリ配下のサブディレクトリを正しく検証できていない。

## To-be (あるべき姿)
`doc-validation`フックの設定が更新され、`/_in_box/`フォルダと`plans/`配下のすべてのサブディレクトリ内のMarkdownファイルが、Pull Requestの時点でフォーマットの妥当性を確実にチェックされるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `doc-validation`フックの正規表現を更新する (`Task: A`)

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `/_in_box`フォルダ内、および`plans/`配下のサブディレクトリに不正なフォーマットのファイルを追加したPull Requestで、CIの`doc-validation`チェックが失敗すること。

## 成果物 (Deliverables)
- 更新された`.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-017`
- **作業ブランチ (Feature Branch):** `story/update-pre-commit-config`
