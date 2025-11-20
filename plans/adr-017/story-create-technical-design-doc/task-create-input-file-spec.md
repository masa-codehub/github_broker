# 【Task】入力ファイル仕様の作成

## 親Issue (Parent Issue)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/017-commit-triggered-issue-creation.md`

## As-is (現状)
`/_in_box`に配置するIssueファイルの厳密なフォーマットを定義した仕様書が存在しない。

## To-be (あるべき姿)
`2_input_file_spec.md`が作成され、IssueファイルのYAML Front Matterに関する厳密なデータ規約（キー、データ型、必須/任意、説明、具体例）が定義されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `2_input_file_spec.md`を新規作成し、YAML Front Matterの仕様を記述する。

## 完了条件 (Acceptance Criteria)
- `docs/architecture/adr-017-issue-creator-workflow/2_input_file_spec.md`が作成されていること。

## 成果物 (Deliverables)
- `docs/architecture/adr-017-issue-creator-workflow/2_input_file_spec.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/create-technical-design-doc`
- **作業ブランチ (Feature Branch):** `task/create-input-file-spec`
