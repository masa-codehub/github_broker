---
title: "【Task】`github_broker`用の要求仕様ディレクトリ作成"
labels:
  - "task"
  - "documentation"
  - "refactoring"
  - "P0"
  - "PRODUCT_MANAGER"
---
# 【Task】`github_broker`用の要求仕様ディレクトリ作成

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- story/optimize-file-placement

## As-is (現状)
- `github_broker`に関連する要求仕様ドキュメント（ADR/Design Doc）を配置するための専用ディレクトリが存在しない。

## To-be (あるべき姿)
- リポジトリのルートに`reqs/adr`と`reqs/design-docs`ディレクトリが作成されている。
- 各ディレクトリに`.gitkeep`ファイルが置かれている。

## ユーザーの意図と背景の明確化
ユーザーは、`github_broker`に関連する要求仕様を、既存の`docs/`（実装ドキュメント用）とは明確に区別された場所に集約したい。これにより、要求と実装のドキュメントの分離を図ることを意図している。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `mkdir -p reqs/adr` を実行する。
2. `mkdir -p reqs/design-docs` を実行する。
3. `touch reqs/adr/.gitkeep` を実行する。
4. `touch reqs/design-docs/.gitkeep` を実行する。
5. 変更をコミットする。

## 完了条件 (Acceptance Criteria)
- `reqs/adr`と`reqs/design-docs`ディレクトリが存在すること。

## 成果物 (Deliverables)
- 作成されたディレクトリ構造を含むコミット

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/optimize-file-placement`
- **作業ブランチ (Feature Branch):** `task/create-broker-reqs-dirs`
