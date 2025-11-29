---
title: "【Task】ADR-013を`github_broker`の要求仕様へ移動"
labels:
  - "task"
  - "documentation"
  - "refactoring"
  - "P1"
  - "PRODUCT_MANAGER"
---
# 【Task】ADR-013を`github_broker`の要求仕様へ移動

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- story/optimize-file-placement

## As-is (現状)
- エージェントの役割設定について決定した`ADR-013`が、`docs/adr/`に配置されている。

## To-be (あるべき姿)
- `docs/adr/013-agent-role-configuration.md`が、`reqs/adr/`配下に移動されている。

## ユーザーの意図と背景の明確化
- このADRは`github_broker`の中核機能であるエージェント管理に関する決定であり、`github_broker`の要求仕様として管理されるべきである。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `git mv docs/adr/013-agent-role-configuration.md reqs/adr/` を実行する。
2. 変更をコミットする。

## 完了条件 (Acceptance Criteria)
- 対象ファイルが`reqs/adr/`に存在すること。
- 対象ファイルが元の`docs/adr/`に存在しないこと。

## 成果物 (Deliverables)
- ファイル移動を行ったコミット

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/optimize-file-placement`
- **作業ブランチ (Feature Branch):** `task/move-adr-013`
