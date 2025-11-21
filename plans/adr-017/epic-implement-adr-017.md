# Issue: #2220
Status: Open

# 【Epic】_in_box方式によるIssue自動起票ワークフローの導入

## 親Issue (Parent Issue)
- (起票後に追記)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/017-commit-triggered-issue-creation.md`

## As-is (現状)
現在、IssueはGitHubのUIを通じて手動で作成されており、Issueの品質は`.github/ISSUE_TEMPLATE`と`.github/workflows/issue_validator.yml`によって担保されている。このプロセスは手動であり、コミット内容とIssueが直接関連付いていない。

## To-be (あるべき姿)
`/_in_box`フォルダに置かれたIssueファイルをコミットし、Pull Requestとして`main`ブランチにマージすることで、GitHub Issueが自動的に起票されるワークフローが構築されている。Issue作成のプロセスがGitベースで管理され、`pre-commit`フックによる品質チェックも統合されている。既存のIssueテンプレートとバリデーターは廃止され、Issue作成プロセスが一本化されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1.  Issue自動起票ワークフローの技術設計ドキュメントを作成する (`Story: A`)
2.  `pre-commit`フックの設定を更新し、`/_in_box`フォルダ内のファイルを検証対象に加える (`Story: B`)
3.  `main`ブランチへのマージをトリガーとするIssue自動起票GitHub Actionsワークフローを新規に作成する (`Story: C`)

## 完了条件 (Acceptance Criteria)
- このEpicを構成する全てのStoryの実装が完了していること。
- `/_in_box/`にIssueファイルを追加したPull Requestが`main`にマージされると、ADR-017で定義された仕様通りにIssueが作成され、ファイルが`/_done_box`に移動される一連のプロセスが正常に動作すること。
- Issue作成に失敗した場合は、ファイルが`/_failed_box`に移動すること。
- 関連する意思決定ドキュメント（ADR-017）の要求事項をすべて満たしていることが確認されること。

## 成果物 (Deliverables)
- 更新された`.pre-commit-config.yaml`
- 新規作成された`.github/workflows/issue-creator.yml`
- 削除された`.github/ISSUE_TEMPLATE`ディレクトリと`.github/workflows/issue_validator.yml`ファイル

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-adr-017`
