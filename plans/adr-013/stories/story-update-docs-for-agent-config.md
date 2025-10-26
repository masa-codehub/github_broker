# 【Story】新しい設定に対応したドキュメントを更新する

## 親Issue (Parent Issue)
- #1691

## 子Issue (Sub-Issues)
- (Task起票後に追記)

## Issue: #1694
## Status: Open

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

# 目的とゴール / Purpose and Goals
新しいエージェント設定方法について開発者向けドキュメントを更新し、開発者がスムーズに環境をセットアップできるようにする。

## As-is (現状)
開発者向けドキュメントや設定サンプルファイルに、新しいエージェント設定（`agents.yml`, `AGENT_CONFIG_PATH`）に関する記述が存在しない。

## To-be (あるべき姿)
開発者が新しい設定方法を容易に理解し、プロジェクトをセットアップできるよう、関連ドキュメントが更新されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: 開発者ガイドに、agents.ymlとAGENT_CONFIG_PATHに関する説明を追記する`
2. `Task: .env.sampleファイルにAGENT_CONFIG_PATHのエントリを追加する`

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。
- `.env.sample` と開発者向けドキュメントに、新しい設定方法が明確に記述されていること。

## 成果物 (Deliverables)
- 関連ドキュメント (更新)
- `.env.sample` (更新)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-013`
- **作業ブランチ (Feature Branch):** `story/update-docs-for-agent-config`