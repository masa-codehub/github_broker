# Task: Add Branch Name Validation Logic to Workflow

## 関連Issue (Relation)
- このTaskは Story `story/modify-issue-validator-for-branch-name` の一部です。

## As-is (現状)
- `issue_validator.yml` 内の `validate-issue-body` ジョブのスクリプトに、ラベルに基づいてブランチ名セクションの有無を検証するロジックが存在しません。

## To-be (あるべき姿)
- `validate-issue-body` ジョブのスクリプトが更新され、Issueのラベルをチェックし、`epic`または`story`ラベルがない場合に`## ブランチ名`セクションの存在を検証するロジックが追加されます。

## 完了条件 (Acceptance Criteria)
- [ ] `issue_validator.yml` ファイル内のスクリプトが、指定されたロジック通りに修正されていること。
- [ ] 修正されたYAMLが、linter (例: `actionlint`) によるチェックをパスすること。

## 成果物 (Deliverables)
- `.github/workflows/issue_validator.yml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/modify-issue-validator-for-branch-name`
- **作業ブランチ (Feature Branch):** `task/add-branch-name-validation-logic`

## 優先度 (Priority)
- P0
