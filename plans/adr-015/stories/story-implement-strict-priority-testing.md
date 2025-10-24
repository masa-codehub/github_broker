# 【Story】厳格な優先度バケット方式のテストを実装する

## 親Issue (Parent Issue)
- (Epic起票後に追記)

## 子Issue (Sub-Issues)
- (Task起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/015-strict-priority-bucket-assignment.md`

# 目的とゴール / Purpose and Goals
新しいタスク割り当てロジックがADR-015の検証基準を満たすことを確認するテストを実装する。

## As-is (現状)
現在のテストスイートは、厳格な優先度バケット方式のタスク割り当てロジックを検証していない。

## To-be (あるべき姿)
`TaskService`のテストが更新され、`P0`のIssueが存在する限り`P1`のIssueが割り当てられないこと、および`P0`のIssueがすべてクローズされた後に`P1`のIssueが割り当てられることを検証できるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: P0とP1のIssueでP1が割り当てられないテスト追加`
2. `Task: P0完了後にP1が割り当てられるテスト追加`

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。
- 新しいテストケースが、厳格な優先度バケット方式のロジックを網羅的に検証していること。

## 成果物 (Deliverables)
- `tests/application/test_task_service.py` (更新)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-015`
- **作業ブランチ (Feature Branch):** `story/implement-strict-priority-testing`
