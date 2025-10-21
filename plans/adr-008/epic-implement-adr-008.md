# 目的とゴール
Epic: Implement ADR-008: Issue Branch Name Validation

## 関連Issue (Relation)
- このEpicは ADR #8 に基づいています。

## 完了条件 (Acceptance Criteria)
- `issue_validator.yml`ワークフローが更新されること。
- `story`または`epic`ラベルを持たないIssueで`## ブランチ名`セクションが欠落している場合、`needs-more-info`ラベルが付与され、修正を促すコメントが自動的に投稿され、ワークフローがエラーとして終了すること。

## 実施内容

## 検証結果

## 影響範囲と今後の課題

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-adr-008`
