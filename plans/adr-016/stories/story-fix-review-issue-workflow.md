# 【Story】レビュー修正タスクのワークフロー修正

## 親Issue (Parent Issue)
- (Epic起票後に追記)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/016-fix-review-issue-assignment-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- `github_broker/application/task_service.py`

## As-is (現状)
`task_service.py` には、レビュー修正タスクを処理するためのロジックに3つの欠陥（キャッシュ漏れ、情報取得ロジック欠如、プロンプト切り替えロジック欠如）が存在する。

## To-be (あるべき姿)
`task_service.py` が修正され、レビュー修正タaskを正しくキャッシュし、プロンプト生成に必要な情報を取得し、タスクの種類に応じて適切なプロンプトを生成できるようになる。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: レビュー修正タスクのキャッシュ処理追加` を実行する。
2. `Task: プロンプト生成に必要な情報取得ロジックの追加` を実行する。
3. `Task: プロンプト切り替えロジックの追加` を実行する。
4. `Task: 動作検証のためのログ追加とテストコード修正` を実行する。
5. 統合テストを通じて、Storyの目標が達成されていることを確認する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。
- ADR-016の検証基準を満たしていること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` の修正
- `tests/application/test_task_service.py` の修正・追加

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-016`
- **作業ブランチ (Feature Branch):** `story/fix-review-issue-workflow`
