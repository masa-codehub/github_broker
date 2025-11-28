---
title: "【Story】既存ドキュメントの整理・移動"
labels:
  - "story"
  - "refactor-docs"
  - "P3" # TaskがP2のため+1
  - "PRODUCT_MANAGER"
---
# 【Story】既存ドキュメントの整理・移動

## 親Issue (Parent Issue)
- (Epic起票後に追記)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- (Epicを参照)

## As-is (現状)
- ADRとDesign Docが`docs/`配下に混在しており、`github_broker`と`issue_creator_kit`のどちらに関するものか判別がつきにくい。
- `plans/`フォルダが残っており、現状と合っていない。

## To-be (あるべき姿)
- 全てのADRとDesign Docが内容に基づいて分類され、`github_broker`関連は`reqs/`に、`issue_creator_kit`関連は`issue_creator_kit/reqs/`に移動されている。
- 不要な`plans/`フォルダが削除されている。

## ユーザーの意図と背景の明確化
ユーザーは、まず既存の資産（ADR/Design Doc）を正しく分類・整理することで、後の詳細設計ドキュメント作成の土台を固めたいと考えている。この整理作業を先に行うことで、設計情報の重複や欠落を防ぎ、効率的に作業を進めることを意図している。

## 目標達成までの手順 (Steps to Achieve Goal)
1.  **Task: ADR/Design Docの棚卸しリスト作成:** 全ドキュメントを確認し、所属を明確化する。
2.  **Task: ディレクトリ構造の整理:** 計画に基づき、必要なディレクトリを作成し、不要なディレクトリを削除する。
3.  **Task: ドキュメントの移動:** 棚卸しリストに従い、ファイルを新しい場所へ移動する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `docs/adr`と`docs/design-docs`から、`github_broker`と`issue_creator_kit`に関連するドキュメントがなくなり、それぞれ新しい`reqs`ディレクトリ配下に正しく配置されていること。
- `plans/`フォルダがリポジトリから削除されていること。

## 成果物 (Deliverables)
- ADR/Design Docの棚卸しリスト
- 更新されたディレクトリ構造

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/refactor-docs`
- **作業ブランチ (Feature Branch):** `story/organize-existing-docs`
