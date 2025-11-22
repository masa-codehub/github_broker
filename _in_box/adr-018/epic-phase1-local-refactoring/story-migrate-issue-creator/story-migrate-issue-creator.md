
# 【Story】Issue作成機能を移行する

## 親Issue (Parent Issue)
- `_in_box/adr-018/epic-phase1-local-refactoring.md`

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- Issue作成に関連するロジックとテストが`github_broker/infrastructure/github_actions/`と`tests/infrastructure/github_actions/`に存在する。

## To-be (あるべき姿)
- `github_broker`からIssue作成関連のコードが削除されている。
- `issue_creator_kit`内のClean Architectureの各レイヤーに、責務に基づいてロジックとテストが再配置されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/infrastructure/github_actions/`のコードを`issue_creator_kit`の適切なレイヤーに移動・リファクタリングする。
2. `tests/infrastructure/github_actions/`のテストを`issue_creator_kit/tests/`以下の適切なレイヤーに移動・修正する。
3. `issue-creator`コマンドが、移行されたロジックを実行できるようにエントリーポイントを実装する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `github_broker`の`github_actions`関連のソースコードとテストがすべて`issue_creator_kit`に移行されていること。
- 移行後の`issue_creator_kit`内で、`issue-creator`に関するすべての単体テストがパスすること。

## 成果物 (Deliverables)
- `issue_creator_kit/` に配置されたIssue作成関連のソースコードとテスト

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/adr018-phase1-refactoring`
- **作業ブランチ (Feature Branch):** `story/migrate-issue-creator`
