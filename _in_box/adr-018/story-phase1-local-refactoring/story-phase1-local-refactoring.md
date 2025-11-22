
# 【Story】フェーズ1: ローカルリファクタリングと集約

## 親Issue (Parent Issue)
- `_in_box/adr-018/epic-implement-adr-018.md`

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- Issue作成と検証に関するロジック、テスト、ドキュメントが`github_broker`リポジトリ内の各所に散在している。

## To-be (あるべき姿)
- `github_broker`リポジトリのルートに`issue_creator_kit`ディレクトリが作成され、関連するすべてのコンポーネントがClean Architectureに基づいて集約・再配置されている。
- `github_broker`のCI/CDとpre-commitフックは、ローカルに編集可能モードでインストールされた`issue_creator_kit`パッケージを参照して動作する。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: issue_creator_kitのディレクトリ構造とpyproject.tomlを作成する`
2. `Task: 既存ロジックをissue_creator_kitへ移動・再配置する`
3. `Task: 既存テストをissue_creator_kitへ移動・再配置する`
4. `Task: 既存ドキュメントをissue_creator_kitへ移動する`
5. `Task: github_brokerのCI/CDとpre-commitフックを更新する`
6. `Task: 修正したCIとpre-commitフックの動作を検証する`

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `github_broker`リポジトリのルートに`issue_creator_kit`ディレクトリが作成され、すべての対象コンポーネントが移動されていること。
- `github_broker/infrastructure/document_validation/`および`github_broker/infrastructure/github_actions/`が削除されていること。
- `pip install -e ./issue_creator_kit` を実行した後、`pre-commit`フックが正常に動作すること。
- `pip install -e ./issue_creator_kit` を実行した後、`issue_creator.yml`ワークフローが正常に動作すること。
- 統合テストによってStoryの目標が達成されていることが確認されること。

## 成果物 (Deliverables)
- `issue_creator_kit/` ディレクトリ内のすべてのファイル
- 更新された `.github/workflows/ci.yml`
- 更新された `.github/workflows/issue_creator.yml`
- 更新された `.pre-commit-config.yaml`
- 削除された古いディレクトリ (`github_broker/infrastructure/document_validation/`, `github_broker/infrastructure/github_actions/`)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-018`
- **作業ブランチ (Feature Branch):** `story/phase1-local-refactoring`
