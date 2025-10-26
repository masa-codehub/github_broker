# 【Task】scripts/validate_docs.pyにADRの概要正規表現検証ロジックを追加する

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/014-improve-adr-validation-rules.md`

# 目的とゴール / Purpose and Goals
ADRの概要行が特定の正規表現に一致することを検証するロジックを`scripts/validate_docs.py`に追加し、ADRの命名規則の一貫性を強制する。

## As-is (現状)
`scripts/validate_docs.py`はADRの概要行のフォーマットを検証していない。

## To-be (あるべき姿)
ADR-014で定義された正規表現 `^\\\[ADR-\\d+\\\]` に概要行が一致することを`scripts/validate_docs.py`が検証できるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `scripts/validate_docs.py`を編集し、正規表現 `^\\\[ADR-\\d+\\\]` を用いてADRの概要行を検証するロジックを追加する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- 新しい正規表現検証ロジックが正しく機能すること。

## 成果物 (Deliverables)
- `scripts/validate_docs.py` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/update-adr-validation-logic`
- **作業ブランチ (Feature Branch):** `task/add-adr-summary-regex-validation`
