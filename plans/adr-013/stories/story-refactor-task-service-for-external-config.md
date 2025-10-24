# 【Story】TaskServiceが外部設定を利用できるようにする

## 親Issue (Parent Issue)
- (Epic起票後に追記)

## 子Issue (Sub-Issues)
- (Task起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

# 目的とゴール / Purpose and Goals
`TaskService` をリファクタリングし、ハードコードされた役割定義への依存をなくし、DIコンテナから動的に注入される設定を利用するように変更する。

## As-is (現状)
`TaskService` がハードコードされた `AGENT_ROLES` リストに依存している。

## To-be (あるべき姿)
`TaskService` がDIコンテナを通じて外部ファイルから読み込まれたエージェント設定リストをインジェクションされ、それを利用して動的にタスク割り当てを行えるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: DIコンテナを修正し、AgentConfigLoaderを使ってエージェント設定をプロバイダーとして登録する`
2. `Task: TaskServiceのコンストラクタを修正し、エージェント設定リストをインジェクションできるようにする`
3. `Task: TaskService内のハードコードされたAGENT_ROLESを削除し、インジェクションされた設定を利用するロジックに置き換える`
4. `Task: TaskServiceの単体テストを修正・追加する`

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。
- `TaskService` から静的な役割定義が除去されていること。
- DIコンテナ経由で注入された設定に基づいて、正しくタスクが割り当てられることを確認する単体テストが成功すること。

## 成果物 (Deliverables)
- `github_broker/infrastructure/di_container.py` (更新)
- `github_broker/application/task_service.py` (更新)
- `tests/application/test_task_service.py` (更新)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-013`
- **作業ブランチ (Feature Branch):** `story/refactor-task-service-for-external-config`