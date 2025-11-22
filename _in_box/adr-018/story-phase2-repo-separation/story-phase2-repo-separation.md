
# 【Story】フェーズ2: リポジトリの完全分離

## 親Issue (Parent Issue)
- `_in_box/adr-018/epic-implement-adr-018.md`

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- `issue_creator_kit`のすべてのコードが`github_broker`リポジトリ内にローカルディレクトリとして存在している（フェーズ1完了時点）。

## To-be (あるべき姿)
- `issue-creator-kit`が独立したGitHubリポジトリとして作成されている。
- `github_broker`のCI/CDとpre-commitフックは、`git+https://...`経由で`issue-creator-kit`パッケージをインストールして利用する。
- `github_broker`リポジトリからローカルの`issue_creator_kit`ディレクトリが削除されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: issue-creator-kitのGitHubリポジトリを作成する`
2. `Task: フェーズ1の成果物を新しいリポジトリにプッシュする`
3. `Task: issue-creator-kitリポジトリのCIを設定する`
4. `Task: github_brokerの参照をgit+https方式に最終化する`
5. `Task: github_brokerからローカルディレクトリを削除し動作を検証する`

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `issue-creator-kit`という名前の新しいGitHubリポジトリが作成され、コードがプッシュされていること。
- `issue-creator-kit`リポジトリのCIが正常に動作し、テストがすべてパスすること。
- `github_broker`の`pre-commit`フックが、`issue-creator-kit`を`git+https`でインストールした上で、ドキュメント検証を正常に実行できること。
- `github_broker`の`issue_creator.yml`ワークフローが、`issue-creator-kit`を`git+https`でインストールし、Issueを正常に自動起票できること。
- `github_broker`リポジトリのルートから`issue_creator_kit`ディレクトリが削除されていること。

## 成果物 (Deliverables)
- 新しい`issue-creator-kit` GitHubリポジトリ
- 更新された `github_broker` リポジトリの `.github/workflows/` および `.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-018`
- **作業ブランチ (Feature Branch):** `story/phase2-repo-separation`
