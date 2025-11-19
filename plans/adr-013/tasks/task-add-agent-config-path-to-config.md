# 【Task】config.pyにAGENT_CONFIG_PATH設定を追加する

## 親Issue (Parent Issue)
- #1692

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

## Issue: #1696
## Status: Open

# 目的とゴール / Purpose and Goals
アプリケーションの設定ファイルパスを環境変数経由で変更可能にすることで、設定の柔軟性を高める。

## As-is (現状)
`config.py` にエージェント設定ファイルのパスを定義する項目がない。

## To-be (あるべき姿)
`config.py` の `Settings` クラスに `AGENT_CONFIG_PATH` が追加され、環境変数から設定を読み込めるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/infrastructure/config.py` を編集し、`Settings` クラスに `AGENT_CONFIG_PATH: str` を追加する。
2. デフォルト値として `/app/agents.yml` を設定する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- 環境変数 `AGENT_CONFIG_PATH` が設定されている場合にその値を読み込むこと。
- 環境変数が未設定の場合に、デフォルト値が使用されること。

## 成果物 (Deliverables)
- `github_broker/infrastructure/config.py` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/introduce-yaml-based-agent-config`
- **作業ブランチ (Feature Branch):** `task/add-agent-config-path-to-config`
## 子Issue (Sub-Issues)
