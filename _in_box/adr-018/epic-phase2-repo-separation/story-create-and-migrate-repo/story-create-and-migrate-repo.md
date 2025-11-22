
# 【Story】issue-creator-kitリポジトリを作成しコードを移行する

## 親Issue (Parent Issue)
- `_in_box/adr-018/epic-phase2-repo-separation.md`

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/018-decouple-issue-creation-and-validation-logic.md`

## As-is (現状)
- `issue_creator_kit`のコードは`github_broker`リポジトリ内にローカルディレクトリとして存在する。

## To-be (あるべき姿)
- `issue-creator-kit`という名前の新しいGitHubリポジトリが作成されている。
- フェーズ1で作成した`issue_creator_kit`ディレクトリの内容が、新しいリポジトリにプッシュされている。
- 新しいリポジトリでCIが設定され、すべてのテストがパスする。

## 目標達成までの手順 (Steps to Achieve Goal)
1. GitHub上で`issue-creator-kit`リポジトリをプライベートで作成する。
2. `github_broker`リポジトリから`issue_creator_kit`ディレクトリの履歴を抽出し、新しいリポジトリにプッシュする。
3. 新しいリポジトリに、Pythonパッケージ向けの基本的なCIワークフロー（pytestの実行など）を設定する。
4. CIが正常に動作し、すべてのテストがパスすることを確認する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `issue-creator-kit` GitHubリポジトリが作成されていること。
- フェーズ1のコードベースが新しいリポジトリに正しく移行されていること。
- 新しいリポジトリのCIでテストがすべてパスすること。

## 成果物 (Deliverables)
- `issue-creator-kit` GitHubリポジトリ
- `issue-creator-kit`リポジトリ内のCI設定ファイル

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/adr018-phase2-separation`
- **作業ブランチ (Feature Branch):** `story/create-ick-repo`
