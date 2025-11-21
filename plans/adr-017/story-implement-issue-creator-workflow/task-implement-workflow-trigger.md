# Issue: #2227
Status: Open

# 【Task】ワークフローのトリガーとファイル特定ロジックの実装

## 親Issue (Parent Issue)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/017-commit-triggered-issue-creation.md`

## 実装の参照資料 (Implementation Reference Documents)
- `docs/architecture/adr-017-issue-creator-workflow/index.md`

## As-is (現状)
`.github/workflows/`ディレクトリに、`/_in_box/`内のファイルからIssueを自動で起票するためのワークフローファイルが存在しない。

## To-be (あるべき姿)
ADR-017の`決定`事項に従い、`.github/workflows/issue-creator.yml`という名前の新しいワークフローファイルが作成されている。このファイルには、Pull Requestが`main`ブランチにマージされた時（`on: pull_request: { types: [closed], branches: [main] }` かつ `if: github.event.pull_request.merged == true`）にのみジョブが実行されるトリガー条件が定義されている。また、後続のステップで処理対象となる、マージされたPull Requestに含まれる`/_in_box/`内のファイル一覧を取得するロジックが実装されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1.  `.github/workflows/issue-creator.yml`という名前でワークフローファイルを新規作成する。
2.  ADR-017で指定されたトリガー条件（`on: pull_request`...）をワークフローに設定する。
3.  `actions/checkout` を使用して、`main`ブランチの最新のコンテンツをチェックアウトするステップを追加する。
4.  マージされたPull RequestのAPIからファイルリストを取得し、`/_in_box/`で始まるファイルのみをフィルタリングして、後続のジョブで利用できるようにするステップを追加する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たすこと。
- `/_in_box`にファイルを追加したPRをマージした際にワークフローがトリガーされ、対象ファイルの一覧をログに出力できること。

## 成果物 (Deliverables)
- `.github/workflows/issue-creator.yml` (部分実装)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/implement-issue-creator-workflow`
- **作業ブランチ (Feature Branch):** `task/implement-workflow-trigger`
