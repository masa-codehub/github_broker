# 【Task】Issue作成ロジックの実装

## 親Issue (Parent Issue)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/017-commit-triggered-issue-creation.md`

## 実装の参照資料 (Implementation Reference Documents)
- `docs/architecture/adr-017-issue-creator-workflow/index.md`

## As-is (現状)
ワークフローはマージされたPRから`/_in_box/`内のファイルパスを特定できるが、そのファイル内容を解釈してGitHub Issueを作成するロジックは実装されていない。

## To-be (あるべき姿)
ADR-017の`決定`事項に基づき、ワークフローに対象ファイルの内容を読み込み、Issueのタイトル、本文、ラベル、担当者などの情報を抽出して、`gh cli`または`actions/github-script`を用いてGitHub Issueを作成するロジックが実装されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1.  前のステップで特定したファイルリストをループ処理するステップを追加する。
2.  ループ内で、各ファイルの内容を読み込む。
3.  読み込んだ内容からYAML Front Matterをパースし、Issueのメタデータ（タイトル、ラベル、担当者）を抽出する。
4.  YAML Front Matterを除いた残りの部分をIssueの本文として抽出する。
5.  抽出したメタデータと本文を`gh issue create`コマンドの引数として渡し、Issueを作成するステップを実装する。
6.  Issue作成の成否結果を、後続のファイル移動ステップで参照できるようにアウトプットとして設定する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体TestがPassすること。
- ワークフローが実行されると、`/_in_box`内のファイルの内容に基づいたIssueが正しくGitHub上に作成されること。

## 成果物 (Deliverables)
- `.github/workflows/issue-creator.yml` (部分実装)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/implement-issue-creator-workflow`
- **作業ブランチ (Feature Branch):** `task/implement-issue-creation-logic`

## 子Issue (Sub-Issues)

- 
