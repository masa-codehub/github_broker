---
title: "【Task】ディレクトリ構造の整理"
labels:
  - "task"
  - "refactor-docs"
  - "P1"
  - "PRODUCT_MANAGER"
---
# 【Task】ディレクトリ構造の整理

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (Storyを参照)

## As-is (現状)
- ドキュメントを移動するための `reqs/` と `issue_creator_kit/reqs`, `issue_creator_kit/docs` ディレクトリが存在しない。
- 不要な `plans/` ディレクトリが残っている。

## To-be (あるべき姿)
- リポジトリのルートに `reqs/` ディレクトリが作成されている。
- `issue_creator_kit/` 配下に `reqs/` と `docs/` ディレクトリが作成されている。
- `plans/` ディレクトリがリポジトリから削除されている。

## ユーザーの意図と背景の明確化
ユーザーは、実際のファイル移動作業の前に、受け皿となるディレクトリ構造を先に整えておきたい。また、現在使われていない`plans/`フォルダをこのタイミングで削除し、リポジトリをクリーンな状態に保つことを意図している。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `mkdir reqs` を実行する。
2. `mkdir -p issue_creator_kit/reqs` を実行する。
3. `mkdir -p issue_creator_kit/docs` を実行する。
4. `rm -rf plans` を実行する。
5. `touch _in_box/.gitkeep` を実行する。
6. 上記の変更をコミットする。

## 完了条件 (Acceptance Criteria)
- `reqs/`, `issue_creator_kit/reqs/`, `issue_creator_kit/docs/` ディレクトリが正しく作成されていること。
- `plans/` ディレクトリが完全に削除されていること。
- `_in_box/` ディレクトリに `.gitkeep` ファイルが存在すること。

## 成果物 (Deliverables)
- 更新されたリポジトリのディレクトリ構造

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/organize-existing-docs`
- **作業ブランチ (Feature Branch):** `task/reorganize-directories`
