---
title: "【Task】`plans/` ディレクトリの削除"
labels:
  - "task"
  - "documentation"
  - "refactoring"
  - "P0"
  - "PRODUCT_MANAGER"
---
# 【Task】`plans/` ディレクトリの削除

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- story/optimize-file-placement

## As-is (現状)
- リポジトリのルートに`plans/`ディレクトリが存在する。

## To-be (あるべき姿)
- `plans/`ディレクトリがリポジトリから完全に削除されている。

## ユーザーの意図と背景の明確化
ユーザーは、現在使用されていない`plans/`ディレクトリを削除することで、リポジトリをクリーンな状態に保ち、`_in_box`が唯一の計画管理ディレクトリであることを明確にしたいと考えている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `git rm -rf plans` を実行する。
2. 変更をコミットする。

## 完了条件 (Acceptance Criteria)
- `plans/`ディレクトリがリポジトリのファイルツリーに存在しないこと。
- `git status`で、削除以外の変更がないこと。

## 成果物 (Deliverables)
- `plans/`ディレクトリが削除されたコミット

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/optimize-file-placement`
- **作業ブランチ (Feature Branch):** `task/delete-plans-directory`
