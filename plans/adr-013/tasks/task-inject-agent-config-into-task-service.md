# 【Task】TaskServiceのコンストラクタを修正し、エージェント設定リストをインジェクションできるようにする

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

# 目的とゴール / Purpose and Goals
`TaskService` が外部の設定に依存できるように、コンストラクタを通じて設定情報を注入（インジェクション）可能にする。

## As-is (現状)
`TaskService` のコンストラクタが、エージェント設定を受け取る引数を持っていない。

## To-be (あるべき姿)
`TaskService` のコンストラクタが、エージェント定義のリストを引数として受け取り、インスタンス変数として保持するよう修正されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py` を編集する。
2. `TaskService` の `__init__` メソッドに、エージェント設定リストを受け取るための新しい引数を追加する。
3. 受け取ったリストを、`self.agent_definitions` のようなインスタンス変数に格納する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- `TaskService` のインスタンス化時に、エージェント設定リストを渡せるようになっていること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/refactor-task-service-for-external-config`
- **作業ブランチ (Feature Branch):** `task/inject-agent-config-into-task-service`