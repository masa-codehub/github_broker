
# 【Epic】ADR-018 フェーズ1: ローカルリファクタリングと集約

## 親Issue (Parent Issue)
- (なし)

## 子Issue (Sub-Issues)
- `_in_box/adr-018/epic-phase1-local-refactoring/story-build-foundation.md`
- `_in_box/adr-018/epic-phase1-local-refactoring/story-migrate-doc-validator.md`
- `_in_box/adr-018/epic-phase1-local-refactoring/story-migrate-issue-creator.md`
- `_in_box/adr-018/epic-phase1-local-refactoring/story-update-and-verify-references.md`
- `_in_box/adr-018/epic-phase1-local-refactoring/story-cleanup-old-files.md`

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
ADR-018の決定に基づき、`github_broker`リポジトリから汎用的な責務を分離するリファクタリングの第一段階に着手します。現状の分析として、ドキュメントの構文検証 (`pre-commit`フック) やIssueの自動起票 (`_in_box`利用) といったCI/CD関連ロジックが、Issue割り当てという中核機能と混在しています。これは単一責任の原則に反しており、結果としてコードの見通しを悪化させ、メンテナンス性を低下させている問題があります。

## To-be (あるべき姿)
As-isで分析した問題を解決するため、まず`github_broker`リポジトリ内に`issue_creator_kit`という新しいパッケージの領域を作成します。最終目標であるリポジトリ分離の前段階として、関連する全コンポーネントをADR-018で定義されたClean Architectureに基づき集約・再配置します。これにより、責務の分離を明確にし、将来的な拡張性を確保することを目的とします。最終的に、`github_broker`のCI/CDとフックは、このローカルパッケージを参照して動作するようになります。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `issue_creator_kit`のディレクトリ構造と`pyproject.toml`を作成する。
2. 既存のドキュメント検証ロジックを`issue_creator_kit`へ移動・再配置する。
3. 既存のIssue作成ロジックを`issue_creator_kit`へ移動・再配置する。
4. 関連するテストを`issue_creator_kit`へ移動・再配置する。
5. 関連するドキュメントを`issue_creator_kit`へ移動する。
6. `github_broker`のCI/CDとpre-commitフックを、新しいエントリーポイントを参照するように更新する。
7. 修正したCIとpre-commitフックがすべて正常に動作することを検証する。

## 完了条件 (Acceptance Criteria)
- このEpicを構成する全てのStory/Taskの実装が完了していること。
- `github_broker`リポジトリのルートに`issue_creator_kit`ディレクトリが作成され、すべての対象コンポーネントが移動されていること。
- `github_broker/infrastructure/document_validation/`および`github_broker/infrastructure/github_actions/`が削除されていること。
- `pip install -e ./issue_creator_kit` を実行した後、`pre-commit`フックが正常に動作すること。
- `pip install -e ./issue_creator_kit` を実行した後、`issue_creator.yml`ワークフローが正常に動作すること。
- 統合テストを通じて、ADR-018のフェーズ1に関する要求事項がすべて満たされていることが確認されること。

## 成果物 (Deliverables)
- `issue_creator_kit/` ディレクトリ内のすべてのファイル
- 更新された `.github/workflows/ci.yml`
- 更新された `.github/workflows/issue_creator.yml`
- 更新された `.pre-commit-config.yaml`
- 削除された古いディレクトリ (`github_broker/infrastructure/document_validation/`, `github_broker/infrastructure/github_actions/`)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/adr018-phase1-refactoring`
