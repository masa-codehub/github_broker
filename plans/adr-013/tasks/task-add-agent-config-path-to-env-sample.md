# 【Task】.env.sampleファイルにAGENT_CONFIG_PATHのエントリを追加する

## 親Issue (Parent Issue)
- #1694

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

## Issue: #1705
## Status: Open

# 目的とゴール / Purpose and Goals
開発者が新しい環境変数を認識し、設定のデフォルト値を容易に把握できるように、`.env.sample` ファイルを更新する。

## As-is (現状)
`.env.sample` に、エージェント設定ファイルのパスを指定するための環境変数の記述がない。

## To-be (あるべき姿)
`.env.sample` に `AGENT_CONFIG_PATH` のエントリが追加され、開発者がどの環境変数を設定すべきか容易に理解できるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `.build/context/.env.sample` ファイルを編集する。
2. `AGENT_CONFIG_PATH=/app/agents.yml` のようなサンプルエントリを追記する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- `.env.sample` ファイルが正しく更新されていること。

## 成果物 (Deliverables)
- `.build/context/.env.sample` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/update-docs-for-agent-config`
- **作業ブランチ (Feature Branch):** `task/add-agent-config-path-to-env-sample`
## 子Issue (Sub-Issues)
