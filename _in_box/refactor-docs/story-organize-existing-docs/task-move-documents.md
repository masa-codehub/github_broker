---
title: "【Task】ドキュメントの移動"
labels:
  - "task"
  - "refactor-docs"
  - "P2"
  - "PRODUCT_MANAGER"
---
# 【Task】ドキュメントの移動

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (Storyを参照)

## As-is (現状)
- `github_broker`と`issue_creator_kit`に関するADRとDesign Docが`docs/adr`と`docs/design-docs`に混在している。

## To-be (あるべき姿)
- `doc-inventory.md`（棚卸しリスト）に基づき、全ての関連ドキュメントが新しいディレクトリに移動されている。
  - `github_broker`関連 -> `reqs/`
  - `issue_creator_kit`関連 -> `issue_creator_kit/reqs/`

## ユーザーの意図と背景の明確化
ユーザーは、このタスクでフェーズ１の最終目的であるドキュメントの物理的な整理を完了させることを意図している。棚卸しリストという明確なエビデンスに基づいて作業することで、抜け漏れなく、正確にファイルを移動させることが重要である。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `_in_box/refactor-docs/story-organize-existing-docs/doc-inventory.md` を参照する。
2. リストに従い、`git mv` コマンドを使用してファイルを一つずつ移動する。
3. すべてのファイルの移動が完了したら、変更をコミットする。

## 完了条件 (Acceptance Criteria)
- 棚卸しリストに記載されたすべてのドキュメントが、指定された新しいパスに移動されていること。
- `docs/adr`と`docs/design-docs`配下から、移動対象のファイルがなくなっていること。

## 成果物 (Deliverables)
- 更新されたリポジトリのファイル配置

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/organize-existing-docs`
- **作業ブランチ (Feature Branch):** `task/move-documents`
