
# 【Story】github_brokerの参照を最終化し検証する

## 親Issue (Parent Issue)
- `_in_box/adr-_in_box/adr-018/epic-phase2-repo-separation.md`

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## As-is (現状)
- `github_broker`はローカルの`issue_creator_kit`ディレクトリを参照している。
- `issue_creator_kit`リポジトリは独立して存在する。

## To-be (あるべき姿)
- `github_broker`のCI/CDとpre-commitフックは、`git+https://...`経由で`issue_creator_kit`リポジトリの特定のGitタグを参照してパッケージをインストールする。
- `github_broker`リポジトリからローカルの`issue_creator_kit`ディレクトリが完全に削除されている。
- すべてのCI/CDジョブとpre-commitフックが正常に動作する。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `issue-creator_kit`リポジトリで最初のバージョンタグ（例: `v1.0.0`）を作成する。
2. `github_broker`の`.github/workflows/`と`.pre-commit-config.yaml`を修正し、`pip install -e`から`pip install git+https://...@v1.0.0`形式の参照に切り替える。
3. `github_broker`リポジトリから`issue_creator_kit`ディレクトリを`git rm -r`で削除する。
4. すべてのCI/CDとpre-commitフックが、リモートリポジトリを参照して正常に動作することを最終確認する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `github_broker`のCI/CDとpre-commitフックが、`git+https`経由で`issue_creator_kit`をインストールし、正常に動作すること。
- `github_broker`リポジトリから`issue_creator_kit`ディレクトリが削除されていること。

## 成果物 (Deliverables)
- 更新された `github_broker`の`.github/workflows/*`
- 更新された `github_broker`の`.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/adr018-phase2-separation`
- **作業ブランチ (Feature Branch):** `story/finalize-ick-references`
