# 【Task】P0とP1のIssueでP1が割り当てられないテスト追加

## 親Issue (Parent Issue)
- #1741

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/015-strict-priority-bucket-assignment.md`

## Issue: #1746
## Status: Open

# 目的とゴール / Purpose and Goals
厳格な優先度バケット方式が正しく機能することを検証するため、`P0`のIssueが存在する限り`P1`のIssueがエージェントに割り当てられないことを確認するテストケースを追加する。

## As-is (現状)
現在のテストスイートは、厳格な優先度バケット方式のタスク割り当てロジックを検証していない。

## To-be (あるべき姿)
`TaskService`のテストが更新され、`P0`のIssueが存在する限り`P1`のIssueが割り当てられないことを検証できるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `tests/application/test_task_service.py`を編集し、`P0`と`P1`のIssueが両方オープンな状態で、`P1`のIssueが割り当てられないことを確認するテストケースを追加する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- 新しいテストケースが、厳格な優先度バケット方式のロジックを網羅的に検証していること。

## 成果物 (Deliverables)
- `tests/application/test_task_service.py` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/implement-strict-priority-testing`
- **作業ブランチ (Feature Branch):** `task/add-p0-p1-no-assignment-test`

## 子Issue (Sub-Issues)
