# 【Task】scripts/validate_docs.pyのテストにDesign Docの新しい検証ケースを追加する

## 親Issue (Parent Issue)
- #1719

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/014-improve-adr-validation-rules.md`

## Issue: #1726
## Status: Open

# 目的とゴール / Purpose and Goals
Design Docの新しい検証ルールが正しく機能することを保証するため、`scripts/validate_docs.py`のテストにDesign Docの新しい検証ケースを追加する。

## As-is (現状)
`scripts/validate_docs.py`のテストは、Design Docの新しい検証ルールに対応していない。

## To-be (あるべき姿)
`scripts/validate_docs.py`のテストが更新され、Design Docの新しい検証ルールが正しく機能することを網羅的に検証できるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `tests/scripts/test_validate_docs.py`を編集し、Design Docの必須セクション検証および概要正規表現検証のテストケースを追加する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- Design Docの新しい検証ルールに対するテストが網羅的に書かれていること。

## 成果物 (Deliverables)
- `tests/scripts/test_validate_docs.py` (更新)

## 実施内容 / Implementation
(ここに具体的な実装手順を記述)

## 検証結果 / Validation Results
(ここに検証結果を記述)

## 影響範囲と今後の課題 / Impact and Future Issues
(特になし)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/strengthen-doc-validation-tests`
- **作業ブランチ (Feature Branch):** `task/add-design-doc-validation-test-cases`
