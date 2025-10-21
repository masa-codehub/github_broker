# 目的とゴール
Story: Modify issue_validator.yml Workflow

## 関連Issue (Relation)
- このStoryは Epic `epic/implement-adr-008` の一部です。

## As-is (現状)
- `issue_validator.yml` ワークフローは、Issue本文の `## ブランチ名` セクションの存在をチェックしていません。

## To-be (あるべき姿)
- `issue_validator.yml` ワークフローが、`epic` または `story` ラベルを持たないIssueに対して `## ブランチ名` セクションの存在をチェックするようになります。

## 完了条件 (Acceptance Criteria)
- [ ] `validate-issue-body` ジョブが、ブランチ名セクションが欠落しているIssueを正しく識別し、失敗すること。
- [ ] ワークフローの変更が、既存の他の検証ルールに影響を与えないこと。

## 実施内容

## 検証結果

## 成果物 (Deliverables)
- `.github/workflows/issue_validator.yml`

## 影響範囲と今後の課題

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-008`
- **作業ブランチ (Feature Branch):** `story/modify-issue-validator-for-branch-name`

## 優先度 (Priority)
- P0
