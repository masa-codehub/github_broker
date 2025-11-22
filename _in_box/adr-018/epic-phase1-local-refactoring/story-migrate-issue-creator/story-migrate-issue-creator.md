
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
ドキュメント検証機能の移行に続き、Issue作成機能の移行に着手します。ADR-018の決定に基づき、現在`github_broker/infrastructure/github_actions/`ディレクトリおよび`tests/infrastructure/github_actions/`に存在するIssue自動起票関連の全ロ-ジックとテストが、このStoryの移行対象となります。現状のコードはGitHub Actionsという特定の実行環境と密結合している可能性があります。

## To-be (あるべき姿)
As-isで特定されたコード群を、`issue_creator_kit`パッケージ内に移行します。ドキュメント検証機能と同様に、domain（Issueのデータ構造）、application（起票オーケストレーション）、infrastructure（GitHub CLI呼び出し）、interface（CLI）の各レイヤーの責務に従ってリファクタリングされます。これにより、特定のCI環境への依存を低減し、機能単体での再利用性とテスト容易性が向上した状態になります。

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
