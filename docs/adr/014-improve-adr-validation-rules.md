# 概要 / Summary
[ADR-014] ドキュメント検証規約の改善

- Status: 提案中
- Date: 2025-10-23

## 状況 / Context

現在のドキュメント検証スクリプト (`scripts/validate_docs.py`) は、ADRおよびDesign Docファイルに、ごく基本的なセクションが存在することのみをチェックしており、ドキュメントの品質を保証するには不十分な状態です。

一方で、エージェントの行動規範 `.gemini/AGENTS/SYSTEM_ARCHITECT.md` には、より包括的で実用的なドキュメントテンプレートが定義されていますが、そのセクション名や形式が検証規約と一致していませんでした。

この状況を解決するため、両者の良い部分を統合し、より高品質で一貫性のある「最終版テンプレート」を新しい公式規約として定め、それをシステムで強制する方針を決定します。

## 決定 / Decision

ADRとDesign Docの公式テンプレートを以下のように最終決定し、検証スクリプト `scripts/validate_docs.py` を、この新しい規約を強制するように修正します。

### 1. ADR (`docs/adr/*.md`) の最終テンプレートと検証ロジック

**必須セクション:**
ADRは、以下の文字列がファイル内に存在することを必須とします。
1.  `# 概要 / Summary`
2.  `- Status:`
3.  `- Date:`
4.  `## 状況 / Context`
5.  `## 決定 / Decision`
6.  `## 結果 / Consequences`
7.  `### メリット (Positive consequences)`
8.  `### デメリット (Negative consequences)`
9.  `## 検証基準 / Verification Criteria`
10. `## 実装状況 / Implementation Status`

**追加の検証ロジック:**
- `# 概要 / Summary` の直後の行が、正規表現 `^\\\[ADR-\\d+\\\]` に一致すること（例: `[ADR-001]...`）を検証するロジックを追加します。

### 2. Design Doc (`docs/design-docs/*.md`) の最終テンプレートと検証ロジック

**必須セクション:**
Design Docは、以下の文字列がファイル内に存在することを必須とします。
1.  `# 概要 / Overview`
2.  `## 背景と課題 / Background`
3.  `## ゴール / Goals`
4.  `### 機能要件 / Functional Requirements`
5.  `### 非機能要件 / Non-Functional Requirements`
6.  `## 設計 / Design`
7.  `### ハイレベル設計 / High-Level Design`
8.  `### 詳細設計 / Detailed Design`
9.  `## 検討した代替案 / Alternatives Considered`
10. `## セキュリティとプライバシー / Security & Privacy`
11. `## 未解決の問題 / Open Questions & Unresolved Issues`
12. `## 検証基準 / Verification Criteria`
13. `## 実装状況 / Implementation Status`

**追加の検証ロジック:**
- `# 概要 / Overview` の直後の行が、`デザインドキュメント:` で始まることを検証するロジックを追加します。

## 結果 / Consequences

### メリット (Positive consequences)
- **ドキュメント品質の標準化:** ADRとDesign Docの両方で、高品質で一貫性のあるフォーマットが保証されます。
- **追跡可能性と検証可能性の向上:** `Status`や`検証基準`などが必須となることで、すべての設計決定が追跡・検証可能になります。
- **規約の明確化:** 作成者が従うべきルールが明確になり、ドキュメント作成の効率と質が向上します。

### デメリット (Negative consequences)

## 検証基準 / Verification Criteria

- 新しい検証規約に準拠していないADRまたはDesign Docファイルをコミットしようとすると、`pre-commit`フックがエラーを出力して失敗すること。
- 新しい検証規約の必須セクションをすべて満たしたADRおよびDesign Docファイルは、コミットが成功すること。

## 実装状況 / Implementation Status
未着手