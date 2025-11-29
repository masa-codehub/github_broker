---
title: "【Task】ADR-006を`github_broker`の要求仕様へ移動"
labels:
  - "task"
  - "documentation"
  - "refactoring"
  - "P1"
  - "PRODUCT_MANAGER"
---
# 【Task】ADR-006を`github_broker`の要求仕様へ移動

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- story/optimize-file-placement

## As-is (現状)
- ハイブリッドなアーキテクチャを決定した`ADR-006`が、`docs/adr/`に配置されている。

## To-be (あるべき姿)
- `docs/adr/006-hybrid-polling-and-server-side-logic.md`が、`reqs/adr/`配下に移動されている。

## ユーザーの意図と背景の明確化
- このADRは`github_broker`のアーキテクチャに関する重要な変更決定であり、`github_broker`の要求仕様として管理されるべきである。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `git mv docs/adr/006-hybrid-polling-and-server-side-logic.md reqs/adr/` を実行する。
2. 変更をコミットする。

## 完了条件 (Acceptance Criteria)
- 対象ファイルが`reqs/adr/`に存在すること。
- 対象ファイルが元の`docs/adr/`に存在しないこと。

## 成果物 (Deliverables)
- ファイル移動を行ったコミット

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/optimize-file-placement`
- **作業ブランチ (Feature Branch):** `task/move-adr-006`
