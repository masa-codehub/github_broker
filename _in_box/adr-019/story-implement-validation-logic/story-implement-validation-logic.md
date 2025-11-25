---
title: "【Story】Issueデータ検証ロジックの実装"
labels:
  - "story"
  - "adr-019"
  - "P1"
  - "PRODUCT_MANAGER"
---
# 【Story】Issueデータ検証ロジックの実装

## 親Issue (Parent Issue)
- `epic-implement-adr-019` (起票後にIssue番号を記載)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/019-fix-issue-creator-workflow.md`

## As-is (現状)
`issue_creator_kit`パッケージには、Markdownファイルのフロントマターの構造や型を検証する専用のサービスが存在しない。

## To-be (あるべき姿)
`issue_creator_kit/application/validation_service.py`に、MarkdownファイルのフロントマターがADR-019で定義された要件（`title`の存在、`labels`の型など）を満たしているかを検証する`validate_frontmatter`関数が実装されている。また、そのロジックを網羅する単体テストが存在し、品質が担保されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `validate_frontmatter`関数を含む`ValidationService`を実装する (`Task: Create Validation Service`)。
2. `ValidationService`の正常系・異常系を網羅する単体テストを実装する (`Task: Implement Unit Tests`)。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `pytest`を実行し、追加された単体テストがすべてパスすること。

## 成果物 (Deliverables)
- `issue_creator_kit/application/validation_service.py`
- `tests/application/test_validation_service.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-019-validation`
- **作業ブランチ (Feature Branch):** `story/implement-validation-logic`
