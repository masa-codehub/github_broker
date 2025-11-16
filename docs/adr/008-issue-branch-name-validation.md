# 概要 / Summary
[ADR-008] issue-branch-name-validation

- Status: Completed
- Date: 2025-10-19

## 状況 / Context

現在の`issue_validator.yml`ワークフローは、特定のセクション（背景、目的、完了条件）の存在を検証しているが、ブランチ名の記載は必須としていない。これにより、開発者がIssueからブランチ名を特定できず、手動での確認や修正依頼が発生し、開発効率が低下している。特に、`story`や`epic`のような上位レベルのIssueはブランチ名を直接持たないことが多いため、これらのラベルが付与されたIssueは検証の対象外とする。

## 決定 / Decision
Issueの品質を向上させ、開発プロセスの手戻りを削減するため、`story`または`epic`ラベルが付与されていないすべてのIssueに対して、Issue本文に`## ブランチ名`セクションの存在を必須とする。この検証はGitHub Actionsワークフロー`issue_validator.yml`の`validate-issue-body`ジョブに組み込む。

## 結果 / Consequences

### メリット (Positive consequences)
*   `issue_validator.yml`が更新され、`validate-issue-body`ジョブに新しい検証ロジックが追加される。
*   `story`または`epic`ラベルを持たないIssueで`## ブランチ名`セクションが欠落している場合、`needs-more-info`ラベルが付与され、修正を促すコメントが自動的に投稿される。
*   ワークフローはエラーとして終了し、Issue作成者に修正を促す。
*   開発者はIssue作成時にブランチ名の記載を意識するようになり、Issueの品質が向上する。

### デメリット (Negative consequences)
*   ワークフローの変更とメンテナンスが必要。

## 検証基準 / Verification Criteria
- `story`または`epic`ラベルが付いていないIssueで、`## ブランチ名`セクションが無いものを新規作成または更新すると、GitHub Actionsの`validate-issue-body`ジョブが失敗すること。
- 上記条件でジョブが失敗した際、対象のIssueに`needs-more-info`ラベルが付与され、修正を促すコメントが投稿されること。
- `## ブランチ名`セクションが存在するIssue、または`story`/`epic`ラベルが付いているIssueは、`validate-issue-body`ジョブが成功すること。

## 実装状況 / Implementation Status
- 完了