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
*   Issueの品質が自動的に向上し、開発プロセスの手戻りが削減される。
*   開発者がブランチ名を意識してIssueを作成するようになる。
*   自動コメントとラベル付与により、修正が促され、Issue作成者の学習を支援する。

### デメリット (Negative consequences)
*   ワークフローの変更とメンテナンスが必要。

## 検証基準 / Verification Criteria
*   `issue_validator.yml`が更新され、`validate-issue-body`ジョブに新しい検証ロジックが追加される。
*   `story`または`epic`ラベルを持たないIssueで`## ブランチ名`セクションが欠落している場合、`needs-more-info`ラベルが付与され、修正を促すコメントが自動的に投稿される。
*   ワークフローはエラーとして終了し、Issue作成者に修正を促す。
*   開発者はIssue作成時にブランチ名の記載を意識するようになり、Issueの品質が向上する。

## 実装状況 / Implementation Status
完了