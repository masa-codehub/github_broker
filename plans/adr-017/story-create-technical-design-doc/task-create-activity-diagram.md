# Issue: #2222
Status: Open

# 【Task】ワークフロー・アクティビティ図の作成

## 親Issue (Parent Issue)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/017-commit-triggered-issue-creation.md`

## As-is (現状)
ワークフローの処理フローと条件分岐を視覚化したアクティビティ図が存在しない。

## To-be (あるべき姿)
`1_workflow_activity_diagram.md`が作成され、スイムレーン付きのアクティビティ図によって、Pull Requestのマージからファイルの移動・コミットまでの全ステップが表現されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `1_workflow_activity_diagram.md`を新規作成し、Mermaid.js形式でスイムレーン付きアクティビティ図を記述する。

## 完了条件 (Acceptance Criteria)
- `docs/architecture/adr-017-issue-creator-workflow/1_workflow_activity_diagram.md`が作成されていること。

## 成果物 (Deliverables)
- `docs/architecture/adr-017-issue-creator-workflow/1_workflow_activity_diagram.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/create-technical-design-doc`
- **作業ブランチ (Feature Branch):** `task/create-activity-diagram`

## 子Issue (Sub-Issues)

- 
