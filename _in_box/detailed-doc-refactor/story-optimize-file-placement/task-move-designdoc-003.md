---
title: "【Task】DesignDoc-003を`github_broker`の要求仕様へ移動"
labels:
  - "task"
  - "documentation"
  - "refactoring"
  - "P1"
  - "PRODUCT_MANAGER"
---
# 【Task】DesignDoc-003を`github_broker`の要求仕様へ移動

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- story/optimize-file-placement

## As-is (現状)
- プロンプトテンプレートの更新について記述した`DesignDoc-003`が、`docs/design-docs/`に配置されている。

## To-be (あるべき姿)
- `docs/design-docs/003-prompt-template-updates.md`が、`reqs/design-docs/`配下に移動されている。

## ユーザーの意図と背景の明確化
- このドキュメントは`github_broker`のエージェントが使用するプロンプトに関するものであり、その要求仕様として管理されるべきである。

## 目標達成までの手順 (Steps to Achieve Goal)
<<<<<<< HEAD
1. `git mv docs/design-docs/003-prompt-template-updates.md reqs/design-docs/` を実行する。
=======
1. `git mv docs/design-docs/003-prompt-template-updates.md reqs/design-docs/003-prompt-template-updates.md` を実行する。
>>>>>>> 1513999 (feat(plan): Refine plan to eliminate document content duplication)
2. 変更をコミットする。

## 完了条件 (Acceptance Criteria)
- 対象ファイルが`reqs/design-docs/`に存在すること。
- 対象ファイルが元の`docs/design-docs/`に存在しないこと。

## 成果物 (Deliverables)
- ファイル移動を行ったコミット

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/optimize-file-placement`
- **作業ブランチ (Feature Branch):** `task/move-designdoc-003`
