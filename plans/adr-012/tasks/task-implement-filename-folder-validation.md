# Issue: #1509
Status: Open
# 【Task】ファイル名とフォルダ構成の検証ロジックを実装する

## 親Issue (Parent Issue)
- #1508

## 子Issue (Sub-Issues)
- (なし)

## As-is (現状)
検証ロジックが存在しない。

## To-be (あるべき姿)
`plans`配下のファイルがADR-012で定義された命名規則とフォルダ構成に従っているかを検証するPython関数が実装される。

## 完了条件 (Acceptance Criteria)
- [ ] ADR-012で定義された全対象ファイル (`docs/adr/*.md`, `docs/design-docs/*.md`, `plans/**/*.md`) を探索する関数が実装されていること。
- [ ] ファイル名が`epic-`, `story-`, `task-`で始まることを検証する関数が実装されていること。
- [ ] `story-*.md`が`stories/`内に、`task-*.md`が`tasks/`内にあることを検証する関数が実装されていること。

## 成果物 (Deliverables)
- Python検証スクリプトの一部

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/create-doc-validation-script`
- **作業ブランチ (Feature Branch):** `task/implement-doc-structure-validation`
