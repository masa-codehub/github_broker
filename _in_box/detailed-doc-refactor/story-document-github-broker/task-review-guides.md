---
title: "【Task】ガイド関連ドキュメント (`docs/guides`) のレビューと軽微な修正"
labels: ["task", "documentation", "refactoring", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】ガイド関連ドキュメント (`docs/guides`) のレビューと軽微な修正

## 親Issue (Parent Issue)
- (Story: `github_broker`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (なし)

## As-is (現状)
- `docs/guides/` 配下の各種ガイドドキュメント（`getting-started.md`, `development-workflow.md`等）が、今回のドキュメント構成リファクタリングの内容を反映していない可能性がある。
- 古いディレクトリ名（例: `plans/`）を参照している、あるいは古い開発プロセスについて言及している箇所が残存している可能性がある。

## To-be (あるべき姿)
- `docs/guides/` 配下の全ドキュメントがレビューされ、今回のリファクタリング内容（新しいディレクトリ構造、コンポーネント分離など）と矛盾しないように、必要な箇所が修正されている。
- 開発者がガイドを読む際に、古い情報に混乱することがなくなる。

## ユーザーの意図と背景の明確化
- ユーザーは、アーキテクチャドキュメントだけでなく、開発者が日常的に参照するガイドラインについても、情報が最新に保たれていることを求めている。プロジェクト全体のドキュメント品質を担保し、一貫性を維持することを意図している。

## **具体的な修正内容**
- **対象ファイル:** `docs/guides/` 配下のすべての `.md` ファイル
- **修正方法:**
  1. 各ファイルの内容を精査する。
  2. 古いディレクトリ名（特に `plans/`）や、古いドキュメント構成への言及があれば、新しい構造（`_in_box/`, `reqs/` など）に修正する。
  3. その他、今回のリファクタリングによって陳腐化した記述があれば、適宜修正する。
  4. 修正が必要なファイルが複数ある場合、それらを一つのコミットにまとめて修正作業を完了させる。

## 完了条件 (Acceptance Criteria)
- `docs/guides/` 配下の全ドキュメントがレビューされ、今回のリファクタリングと整合性が取れていること。

## 成果物 (Deliverables)
- 更新された `docs/guides/` 配下のファイル群を含むコミット

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/review-guides`
