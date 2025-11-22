
# 【Epic】ADR-018 フェーズ2: リポジトリの完全分離

## 親Issue (Parent Issue)
- (なし)

## 依存するIssue (Depends on)
- `_in_box/adr-018/epic-phase1-local-refactoring.md`

## 子Issue (Sub-Issues)
- `_in_box/adr-018/epic-phase2-repo-separation/story-create-and-migrate-repo/story-create-and-migrate-repo.md`
- `_in_box/adr-018/epic-phase2-repo-separation/story-finalize-and-verify-references/story-finalize-and-verify-references.md`

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
ADR-018のフェーズ1が完了し、`issue_creator_kit`は`github_broker`リポジトリ内のローカルディレクトリとして、すべての機能が集約され、正常に動作しています。現状分析として、このままではまだ`github_broker`リポジトリに強く結合しており、ADR-018が目指す「他リポジトリからの再利用」という目標は達成できていません。

## To-be (あるべき姿)
As-isの問題を解決するため、`issue_creator_kit`を完全に独立したGitHubリポジトリとして分離します。`github_broker`は、ローカルパス参照ではなく`git+https://...`経由でこの新しいリポジトリをライブラリとして利用するようになります。これにより、ADR-018の最終目標である「責務の分離」と「再利用性の向上」が完全に達成された状態になります。

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
