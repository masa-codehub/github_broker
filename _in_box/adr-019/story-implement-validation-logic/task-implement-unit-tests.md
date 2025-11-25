---
title: "【Task】単体テストの実装"
labels:
  - "task"
  - "planning"
  - "adr-019"
  - "P1"
  - "BACKENDCODER"
---
# 【Task】単体テストの実装

## 親Issue (Parent Issue)
- `story-implement-validation-logic` (起票後にIssue番号を記載)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/019-fix-issue-creator-workflow.md`

## As-is (現状)
`ValidationService`のテストが存在しない。

## To-be (あるべき姿)
`issue_creator_kit/tests/application/test_validation_service.py`に、`validate_frontmatter`関数のための単体テストが実装されている。テストケースは、ADR-019に記載された以下の正常系・異常系をすべて網羅している。
- 正常系:
  - 必須フィールドがすべて存在する
- 異常系:
  - フロントマターが存在しない
  - `title`フィールドが存在しない
  - `title`フィールドが空文字列
  - `labels`フィールドが文字列のリストではない
  - `related_issues`フィールドが数値のリストではない

## 目標達成までの手順 (Steps to Achieve Goal)
1. `issue_creator_kit/tests/application/test_validation_service.py`ファイルを作成する。
2. `pytest`の`tmp_path`フィクスチャなどを活用し、テスト用のMarkdownファイルを動的に生成する。
3. 上記の正常系・異常系シナリオに対応するテスト関数を実装する。異常系では、`pytest.raises`を使用して特定の例外が送出されることを確認する。

## 完了条件 (Acceptance Criteria)
- TDDのRed-Green-Refactorサイクルに従って実装が完了していること。
- `pytest`を実行し、`test_validation_service.py`に含まれるすべてのテストがパスすること。

## 成果物 (Deliverables)
- `issue_creator_kit/tests/application/test_validation_service.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/implement-validation-logic`
- **作業ブランチ (Feature Branch):** `task/implement-unit-tests-for-validation`
