---
title: "【Task】ADR/Design Docの棚卸しリスト作成"
labels:
  - "task"
  - "refactor-docs"
  - "P0"
  - "PRODUCT_MANAGER"
---
# 【Task】ADR/Design Docの棚卸しリスト作成

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (Storyを参照)

## As-is (現状)
- `docs/adr` と `docs/design-docs` にあるドキュメントが、`github_broker`と`issue_creator_kit`のどちらに関連するものか、ファイル名やパスだけでは判断できない。

## To-be (あるべき姿)
- すべてのADRとDesign Docについて、`github_broker`と`issue_creator_kit`のどちらに属するかが明確に記述されたマークダウン形式のリストが作成されている。

## ユーザーの意図と背景の明確化
ユーザーは、手作業によるドキュメント移動のミスを防ぐため、最初に明確な分類リストを作成することが重要だと考えている。このリストを正として作業を進めることで、後の工程での確認コストを削減し、確実性を高めることを意図している。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `docs/adr` と `docs/design-docs` の全ファイルをリストアップする。
2. 各ファイルの内容を読み、`github_broker` と `issue_creator_kit` のどちらの関心事かを判断する。
3. 判断結果をマークダウンのテーブル形式でまとめる。

## 完了条件 (Acceptance Criteria)
- `docs/adr` と `docs/design-docs` に存在するすべてのファイルがリストに含まれていること。
- 各ファイルに対して、`github_broker` or `issue_creator_kit` の分類が明記されていること。
- 成果物が `_in_box/refactor-docs/story-organize-existing-docs/doc-inventory.md` として保存されていること。

## 成果物 (Deliverables)
- `_in_box/refactor-docs/story-organize-existing-docs/doc-inventory.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/organize-existing-docs`
- **作業ブランチ (Feature Branch):** `task/create-doc-inventory`
