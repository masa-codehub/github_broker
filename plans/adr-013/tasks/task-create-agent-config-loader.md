# 【Task】YAMLファイルを読み込み検証するAgentConfigLoaderコンポーネントを作成する

## 親Issue (Parent Issue)
- #1692

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

## Issue: #1697
## Status: Open

# 目的とゴール / Purpose and Goals
YAMLファイルからエージェント設定を安全に読み込み、アプリケーション内で利用できる形式に変換するためのコンポーネントを作成する。

## As-is (現状)
YAML形式のエージェント設定を読み込み、検証する仕組みが存在しない。

## To-be (あるべき姿)
指定されたパスから `agents.yml` を読み込み、Pydanticモデルを使って内容を検証し、アプリケーションで利用可能なオブジェクトのリストを返す `AgentConfigLoader` クラスが実装されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. エージェント定義のPydanticモデル（`AgentDefinition`）を作成する。
2. YAMLファイルを読み込み、Pydanticモデルのリストにパースする `AgentConfigLoader` を作成する。
3. ファイルが存在しない場合や、内容が不正な場合に例外を発生させる処理を実装する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- `AgentConfigLoader` が、有効なYAMLファイルを正しくパースできること。
- 不正な形式のYAMLや、存在しないファイルパスに対して、適切なエラーをスローすること。

## 成果物 (Deliverables)
- `github_broker/infrastructure/agent/loader.py` (新規)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/introduce-yaml-based-agent-config`
- **作業ブランチ (Feature Branch):** `task/create-agent-config-loader`
## 子Issue (Sub-Issues)
