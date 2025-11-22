
# 【Story】github_brokerの参照更新と検証

## 親Issue (Parent Issue)
- `_in_box/adr-018/epic-phase1-local-refactoring.md`

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- `github_broker`のCI/CDとpre-commitフックは、リポジトリ内のローカルスクリプトを直接参照している。

## To-be (あるべき姿)
- `github_broker`のCI/CDとpre-commitフックは、`pip install -e ./issue_creator_kit`でインストールされた`doc-validator`と`issue-creator`コマンドを呼び出すように変更されている。
- 更新された設定で、すべてのCI/CDジョブとpre-commitフックが正常に動作する。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `.github/workflows/ci.yml`と`issue_creator.yml`を修正し、`pip install -e ./issue_creator_kit`ステップを追加し、コマンド呼び出しを更新する。
2. `.pre-commit-config.yaml`を修正し、`doc-validator`コマンドを呼び出すようにエントリーポイントを変更する。
3. 実際にpre-commitフックを実行し、ローカルで動作を確認する。
4. 変更をプッシュし、CI/CDがGitHub Actions上で正常に動作することを確認する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `.pre-commit-config.yaml`が、ローカルインストールされた`doc-validator`コマンドを正常に実行できること。
- `issue_creator.yml`ワークフローが、ローカルインストールされた`issue-creator`コマンドを正常に実行できること。

## 成果物 (Deliverables)
- 更新された `.github/workflows/ci.yml`
- 更新された `.github/workflows/issue_creator.yml`
- 更新された `.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/adr018-phase1-refactoring`
- **作業ブランチ (Feature Branch):** `story/update-and-verify-references`
