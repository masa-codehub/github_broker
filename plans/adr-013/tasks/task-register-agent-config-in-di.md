# 【Task】DIコンテナを修正し、AgentConfigLoaderを使ってエージェント設定をプロバイダーとして登録する

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

# 目的とゴール / Purpose and Goals
アプリケーション全体で唯一のエージェント設定情報を共有するため、DIコンテナに設定を読み込むプロバイダーを登録する。

## As-is (現状)
DIコンテナが、エージェント設定を管理・提供する機能を持っていない。

## To-be (あるべき姿)
DIコンテナ（`di_container.py`）が `AgentConfigLoader` を利用してYAMLファイルからエージェント設定を読み込み、その結果をシングルトンなプロバイダーとしてコンテナに登録している。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/infrastructure/di_container.py` を編集する。
2. `AgentConfigLoader` をインスタンス化し、設定を読み込む処理を追加する。
3. 読み込んだ設定（エージェント定義のリスト）を、DIコンテナのプロバイダーとして登録する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- DIコンテナからエージェント設定リストが正しく取得できること。

## 成果物 (Deliverables)
- `github_broker/infrastructure/di_container.py` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/refactor-task-service-for-external-config`
- **作業ブランチ (Feature Branch):** `task/register-agent-config-in-di`