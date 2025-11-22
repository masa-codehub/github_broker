
# 【Epic】ADR-018 フェーズ2: リポジトリの完全分離

## 親Issue (Parent Issue)
- (なし)

## 依存するIssue (Depends on)
- `_in_box/adr-018/epic-phase1-local-refactoring.md`

## 子Issue (Sub-Issues)
- `_in_box/adr-018/epic-phase2-repo-separation/story-create-and-migrate-repo.md`
- `_in_box/adr-018/epic-phase2-repo-separation/story-finalize-and-verify-references.md`

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- `issue_creator_kit`のすべてのコードが`github_broker`リポジトリ内にローカルディレクトリとして存在している（フェーズ1完了時点）。

## To-be (あるべき姿)
- `issue_creator_kit`が独立したGitHubリポジトリとして作成されている。
- `github_broker`のCI/CDとpre-commitフックは、`git+https://...`経由で`issue-creator-kit`パッケージをインストールして利用する。
- `github_broker`リポジトリからローカルの`issue_creator_kit`ディレクトリが削除されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `issue-creator-kit`のGitHubリポジトリを作成する。
2. フェーズ1の成果物を新しいリポジトリにプッシュする。
3. `issue-creator-kit`リポジトリのCIを設定し、テストがパスすることを確認する。
4. `github_broker`のCI/CDとpre-commitフックの参照を、ローカルパスから`git+https`方式に最終化する。
5. `github_broker`からローカルの`issue_creator_kit`ディレクトリを削除し、すべての動作を再検証する。

## 完了条件 (Acceptance Criteria)
- このEpicを構成する全てのStory/Taskの実装が完了していること。
- `issue_creator-kit`という名前の新しいGitHubリポジトリが作成され、コードがプッシュされていること。
- `issue-creator-kit`リポジトリのCIが正常に動作し、テストがすべてパスすること。
- `github_broker`の`pre-commit`フックが、`issue-creator-kit`を`git+https`でインストールした上で、ドキュメント検証を正常に実行できること。
- `github_broker`の`issue_creator.yml`ワークフローが、`issue-creator-kit`を`git+https`でインストールし、Issueを正常に自動起票できること。
- `github_broker`リポジトリのルートから`issue_creator_kit`ディレクトリが削除されていること。
- 統合テストを通じて、ADR-018のフェーズ2に関する要求事項がすべて満たされていること。

## 成果物 (Deliverables)
- 新しい`issue-creator-kit` GitHubリポジトリ
- 更新された `github_broker` リポジトリの `.github/workflows/` および `.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/adr018-phase2-separation`
