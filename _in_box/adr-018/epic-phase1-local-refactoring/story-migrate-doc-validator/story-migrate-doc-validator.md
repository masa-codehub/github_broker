
# 【Story】ドキュメント検証機能を移行する

## 親Issue (Parent Issue)
- `_in_box/adr-018/epic-phase1-local-refactoring.md`

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- ドキュメント検証に関連するロジックとテストが`github_broker/infrastructure/document_validation/`と`tests/infrastructure/document_validation/`に存在する。

## To-be (あるべき姿)
- `github_broker`からドキュメント検証関連のコードが削除されている。
- `issue_creator_kit`内のClean Architectureの各レイヤー（domain, application, infrastructure, interface）に、責務に基づいてロジックとテストが再配置されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/infrastructure/document_validation/`のコードを`issue_creator_kit`の適切なレイヤーに移動・リファクタリングする。
2. `tests/infrastructure/document_validation/`のテストを`issue_creator_kit/tests/`以下の適切なレイヤーに移動・修正する。
3. `doc-validator`コマンドが、移行されたロジックを実行できるようにエントリーポイントを実装する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `github_broker`の`document_validation`関連のソースコードとテストがすべて`issue_creator_kit`に移行されていること。
- 移行後の`issue_creator_kit`内で、`doc-validator`に関するすべての単体テストがパスすること。

## 成果物 (Deliverables)
- `issue_creator_kit/` に配置されたドキュメント検証関連のソースコードとテスト

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/adr018-phase1-refactoring`
- **作業ブランチ (Feature Branch):** `story/migrate-doc-validator`
