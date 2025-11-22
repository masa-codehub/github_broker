
# 【Epic】ADR-018: Issue作成と検証ロジックをissue-creator-kitへ分離する

## 親Issue (Parent Issue)
- (なし)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- ドキュメント検証とIssue自動起票のロジックが`github_broker`リポジトリ内に混在しており、責務が肥大化している。
- 汎用的な機能であるにもかかわらず、他リポジトリでの再利用が困難。

## To-be (あるべき姿)
- ドキュメント検証とIssue自動起票のロジックが、独立した`issue-creator-kit`リポジトリに分離されている。
- `github_broker`は、`pip install`を通じて`issue-creator-kit`を利用するようになり、本来の責務に集中できる。
- `issue-creator-kit`は、Clean Architectureに基づいた構造を持ち、メンテナンス性と拡張性が高い。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Story: フェーズ1 - ローカルリファクタリング` を行い、`github_broker`リポジトリ内で`issue-creator-kit`への機能集約を完了させる。
2. `Story: フェーズ2 - リポジトリ分離` を行い、`issue-creator-kit`を完全に独立したリポジトリとして確立する。
3. 全てのCI/CDとローカルフックが正常に動作することを確認し、完了条件を達成する。

## 完了条件 (Acceptance Criteria)
- このEpicを構成する全てのStoryの実装が完了していること。
- 各Storyの成果物を組み合わせた統合テストが成功し、`docs/adr/018-decouple-issue-creation-and-validation-logic.md` の要求事項をすべて満たしていることが確認されること。
- `github_broker`リポジトリから、対象の機能とファイルが完全に削除されていること。
- 新しい`issue-creator-kit`リポジトリが作成され、コードが正常に動作していること。

## 成果物 (Deliverables)
- `issue-creator-kit` GitHubリポジトリ
- 更新された `github_broker` リポジトリの `.github/workflows/` および `.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-adr-018`
