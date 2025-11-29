---
title: "【Task】ADR-017詳細設計ドキュメント群を`issue_creator_kit`配下へ移動"
labels: ["task", "documentation", "refactoring", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】ADR-017詳細設計ドキュメント群を`issue_creator_kit`配下へ移動

## 親Issue (Parent Issue)
- (Story: `issue_creator_kit`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `reqs/adr/017-commit-triggered-issue-creation.md`

## As-is (現状)
- `ADR-017`（コミットトリガーのIssue作成）に関する詳細な設計ドキュメント群（アクティビティ図など）が、`issue_creator_kit/docs/adr-017-workflow/` に配置されている。
- これらのドキュメントは`issue_creator_kit`コンポーネントの核心的な仕様を記述しているが、コンポーネントの外部に置かれているため、発見やメンテナンスが困難になっている。

## To-be (あるべき姿)
- `issue_creator_kit/docs/adr-017-workflow/` ディレクトリ全体が、`issue_creator_kit/docs/adr-017-workflow/` に移動される。
- `issue_creator_kit`に関する全てのドキュメントが、コンポーネント内に集約され、管理しやすくなる。

## ユーザーの意図と背景の明確化
- ユーザーは、コンポーネントの自己完結性を高めるため、その仕様を定義するドキュメントはコンポーネント自身が所有するべきだと考えている。物理的な配置を論理的な所有権と一致させることで、ドキュメントの陳腐化を防ぎ、メンテナンス性を向上させることを意図している。

## **具体的な修正内容**
- **対象ディレクトリ:** `issue_creator_kit/docs/adr-017-workflow/`
- **修正方法:** `git mv`コマンドを使用して、ディレクトリを移動する。

```bash
# 1. issue_creator_kit/docs ディレクトリがなければ作成
mkdir -p issue_creator_kit/docs

# 2. ディレクトリを移動
git mv issue_creator_kit/docs/adr-017-workflow issue_creator_kit/docs/adr-017-workflow
```

## 完了条件 (Acceptance Criteria)
- `issue_creator_kit/docs/adr-017-workflow/` が存在しないこと。
- `issue_creator_kit/docs/adr-017-workflow/` ディレクトリと、その配下のファイルが存在すること。

## 成果物 (Deliverables)
- ファイル移動を行ったコミット

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-issue-creator-kit`
- **作業ブランチ (Feature Branch):** `task/move-adr-017-docs`