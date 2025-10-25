# 【Epic】ADR-016: レビュー修正タスクのワークフロー改善

## 親Issue (Parent Issue)
- (なし)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/016-fix-review-issue-assignment-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- `github_broker/application/task_service.py`
- `github_broker/infrastructure/gemini_executor.py`

## As-is (現状)
ADR-016に記載の通り、レビュー修正タスクがエージェントに割り当てられない問題が存在する。具体的には、キャッシュ漏れ、プロンプト生成に必要な情報取得ロジックの欠如、プロンプト切り替えロジックの欠如の3点が問題となっている。

## To-be (あるべき姿)
レビュー修正タスクが開発タスクと同様にエージェントに割り当てられ、レビューコメントに基づいた修正作業が自動的に実行されるようになる。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Story: レビュー修正タスクのワークフロー修正` を通じて、`task_service.py` の問題を修正する。
2. 統合テストを通じて、ADR-016の検証基準をすべて満たしていることを確認する。

## 完了条件 (Acceptance Criteria)
- このEpicを構成する全てのStoryの実装が完了していること。
- 各Storyの成果物を組み合わせた統合テストが成功し、関連する意思決定ドキュメント（`docs/adr/016-fix-review-issue-assignment-logic.md`）の要求事項をすべて満たしていることが確認されること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` の修正
- `tests/application/test_task_service.py` の修正・追加

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-adr-016`
