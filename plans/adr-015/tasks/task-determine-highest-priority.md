# 【Task】取得した優先度ラベルから現在の最高優先度を特定する関数を実装する

## 親Issue (Parent Issue)
- #1738

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/015-strict-priority-bucket-assignment.md`

## Issue: #1743
## Status: Open

# 目的とゴール / Purpose and Goals
取得したIssueの優先度ラベルリストから、現在オープンなIssueの中で最も高い優先度レベル（例: P0）を特定する関数を実装する。

## As-is (現状)
Issueの優先度ラベルリストから最高優先度を特定する機能が存在しない。

## To-be (あるべき姿)
`TaskService`内に、Issueの優先度ラベルリストを受け取り、最も高い優先度レベル（P0, P1, P2...の順）を返す関数が実装されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py`内に、優先度ラベルのリストをソートし、最も高い優先度を特定する関数を実装する。
2. 優先度ラベルの形式（例: P0, P1）を適切にパースするロジックを考慮する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- 複数の優先度ラベルを持つIssueリストから、正しく最高優先度を特定できること。
- オープンなIssueが存在しない場合に、適切な結果（例: None）を返すこと。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/implement-highest-priority-logic`
- **作業ブランチ (Feature Branch):** `task/determine-highest-priority`

## 子Issue (Sub-Issues)
