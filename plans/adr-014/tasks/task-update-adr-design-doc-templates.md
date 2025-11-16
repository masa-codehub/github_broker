# 【Task】ADRおよびDesign Docのテンプレートを更新する

## 親Issue (Parent Issue)
- #1720

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/014-improve-adr-validation-rules.md`

## Issue: #1728
## Status: Open

# 目的とゴール / Purpose and Goals
ADR-014で定義された新しい検証ルールに合わせて、ADRおよびDesign Docのテンプレートを更新し、作成者が新しい規約に沿ったドキュメントを容易に作成できるようにする。

## As-is (現状)
ADRおよびDesign Docのテンプレートが、ADR-014で定義された新しい検証ルールに対応していない。

## To-be (あるべき姿)
ADRおよびDesign Docのテンプレートが、ADR-014で定義された必須セクションと概要のフォーマットを反映するように更新されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `docs/adr/template.md` (またはそれに相当するファイル) を更新し、新しい必須セクションと概要のフォーマットを反映させる。
2. `docs/design-docs/template.md` (またはそれに相当するファイル) を更新し、新しい必須セクションと概要のフォーマットを反映させる。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- テンプレートが新しい検証ルールを正確に反映していること。

## 成果物 (Deliverables)
- ADRテンプレート (更新)
- Design Docテンプレート (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-adr-014-changes`
- **作業ブランチ (Feature Branch):** `task/update-adr-design-doc-templates`

## 子Issue (Sub-Issues)
