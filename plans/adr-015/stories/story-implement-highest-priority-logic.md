# 【Story】現在の最高優先度を特定するロジックを実装する

## 親Issue (Parent Issue)
- (Epic起票後に追記)

## 子Issue (Sub-Issues)
- (Task起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/015-strict-priority-bucket-assignment.md`

# 目的とゴール / Purpose and Goals
GitHubリポジトリ内のオープン状態のIssueから、最も高い優先度レベル（例: `P0`）を特定するロジックを実装する。

## As-is (現状)
現在のタスク割り当てロジックは、最高優先度を特定する機能を持っていない。

## To-be (あるべき姿)
`TaskService`がGitHub APIを介してオープンなIssueの優先度ラベルを取得し、現在の最高優先度を正確に特定できるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: GitHub APIを呼び出し、オープンなIssueの優先度ラベルを取得する`
2. `Task: 取得した優先度ラベルから現在の最高優先度を特定する関数を実装する`

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。
- オープンなIssueが存在しない場合に、最高優先度が適切に処理されること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` (更新)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-015`
- **作業ブランチ (Feature Branch):** `story/implement-highest-priority-logic`
