# 【Story】Issue自動起票ワークフローの実装

## 親Issue (Parent Issue)
- (起票後に追記)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/017-commit-triggered-issue-creation.md`

## 実装の参照資料 (Implementation Reference Documents)
- `docs/architecture/adr-017-issue-creator-workflow/index.md`

## As-is (現状)
コミット内容に基づいたIssueの自動起票ワークフローは存在しない。

## To-be (あるべき姿)
ADR-017で`決定`された通り、Issue自動起票の機能が**GitHub Actions Workflow**として`.github/workflows/issue-creator.yml`に実装されている。このワークフローは、Pull Requestが`main`ブランチにマージされた時（`on: pull_request: types: [closed], branches: [main]` かつ `if: github.event.pull_request.merged == true`）にのみトリガーされる。ワークフローは`/_in_box/`フォルダ内のファイルを処理し、Issue作成の成功・失敗に応じてファイルを`/_done_box/`または`/_failed_box/`に移動させ、その結果を新しいコミットとして`main`ブランチにプッシュする。

## 目標達成までの手順 (Steps to Achieve Goal)
1.  ワークフローのトリガー条件（`main`へのPRマージ）を定義する (`Task: A`)
2.  マージされたPRに含まれる`/_in_box`内のファイル一覧を取得するロジックを実装する (`Task: A`)
3.  各ファイルからIssueのタイトル、本文、ラベル等を抽出するスクリプトを実装する (`Task: B`)
4.  `gh cli`または`actions/github-script`を使ってIssueを作成するロジックを実装する (`Task: B`)
5.  Issue作成の成否に応じて、ファイルを`/_done_box`または`/_failed_box`に移動するロジックを実装する (`Task: C`)
6.  ファイル移動の変更を`main`ブランチにコミット＆プッシュするロジックを実装する (`Task: C`)

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- ADR-017の`検証基準`に記載された、以下の全ての項目が満たされていること。
    - `/_in_box/`フォルダにIssueファイルを加えるPull Requestが`main`にマージされた際、GitHubリポジトリに新しいIssueが自動的に作成されること。
    - 作成されたIssueのタイトル、本文、ラベル、担当者などが、Issueファイルの内容に基づいて適切に生成されていること。
    - Issue作成後、処理されたIssueファイルが`/_in_box/`から`/_done_box/`に移動し、その変更が`main`ブランチに自動コミットされていること。
    - Issue作成に失敗した場合、対象のIssueファイルが`/_in_box/`から`/_failed_box/`に移動し、その変更が`main`ブランチに自動コミットされていること。
    - ワークフローの実行ログにおいて、エラーなくIssueが作成され、ファイル移動が完了したことが確認できること。

## 成果物 (Deliverables)
- `.github/workflows/issue-creator.yml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-017`
- **作業ブランチ (Feature Branch):** `story/implement-issue-creator-workflow`
