# 【Task】agents.ymlのサンプルファイルを作成する

## 親Issue (Parent Issue)
- #1692

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

## Issue: #1695
## Status: Open

# 目的とゴール / Purpose and Goals
開発者がエージェント設定ファイルのフォーマットを理解し、容易に利用開始できるように、サンプルの設定ファイルを提供する。

## As-is (現状)
エージェント設定ファイルが存在しない。

## To-be (あるべき姿)
開発者が設定ファイルのフォーマットを理解できるよう、サンプルとなる `agents.yml.sample` ファイルが作成されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. ADR-013で定義されたフォーマットに基づき、`agents.yml.sample` ファイルを作成する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- `agents.yml.sample` がプロジェクトのルート、または適切な設定ディレクトリに配置されていること。

## 成果物 (Deliverables)
- `agents.yml.sample`

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/introduce-yaml-based-agent-config`
- **作業ブランチ (Feature Branch):** `task/create-agents-yml-sample`