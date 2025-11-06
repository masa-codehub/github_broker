# 【Task】GitHub APIを呼び出し、オープンなIssueの優先度ラベルを取得する

## 親Issue (Parent Issue)
- #1738

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/015-strict-priority-bucket-assignment.md`

## Issue: #1742
## Status: Open

# 目的とゴール / Purpose and Goals
GitHubリポジトリ内のオープン状態のIssueから、優先度ラベルを含む情報を取得し、タスク割り当てロジックの基礎データを提供する。

## As-is (現状)
タスク割り当てロジックは、Issueの優先度ラベルを直接取得する機能を持っていない。

## To-be (あるべき姿)
`TaskService`がGitHub APIを介してオープンなIssueのリストと、それぞれのIssueに付与されている優先度ラベル（例: P0, P1）を取得できるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/infrastructure/github_client.py`を調査し、Issueのラベルを取得する既存の機能、または新規に機能を追加する。
2. `github_broker/application/task_service.py`からGitHubクライアントを呼び出し、オープンなIssueのリストとラベル情報を取得する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- GitHub APIからIssueの優先度ラベルが正しく取得できること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` (更新)
- `github_broker/infrastructure/github_client.py` (更新の可能性あり)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/implement-highest-priority-logic`
- **作業ブランチ (Feature Branch):** `task/get-issue-priority-labels`
