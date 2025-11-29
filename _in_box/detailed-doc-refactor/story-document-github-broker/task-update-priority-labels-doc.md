---
title: "【Task】`priority-labels.md`に厳格な優先度バケットの動作仕様を追記"
labels: ["task", "documentation", "refactoring", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】`priority-labels.md`に厳格な優先度バケットの動作仕様を追記

## 親Issue (Parent Issue)
- (Story: `github_broker`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `reqs/adr/015-strict-priority-bucket-assignment.md`

## As-is (現状)
- `docs/specs/priority-labels.md`は、P0からP4までの各優先度ラベルの意味を定義しているだけで、これらのラベルがアプリケーションでどのように扱われるかについての説明がない。
- `task_service.py`に実装され、`ADR-015`で決定された「最も高い優先度のタスク群のみが処理対象となる」という重要な動作仕様（厳格な優先度バケット）がドキュメントに反映されていない。

## To-be (あるべき姿)
- `priority-labels.md`に、`github_broker`におけるタスク選択ロジックの概要が追記される。
- 「P0のタスクが存在する場合、P1以下のタスクは処理されない」という、システムの重要な動作原理が明確にドキュメント化される。

## ユーザーの意図と背景の明確化
- ユーザーは、タスクがどのような順序で処理されるのかという、プロジェクトのコアなビジネスルールを開発者や関係者が正しく理解している状態を求めている。この仕様を明記することで、「なぜ自分のタスクが実行されないのか」といった疑問を解消し、運用の透明性を高めることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `docs/specs/priority-labels.md`
- **修正方法:** ファイルの末尾に、以下のMarkdownテキストブロックを**追記**する。

```markdown
## `github_broker`における優先度ベースのタスク選択

`github_broker`システムは、ここに定義された優先度ラベルに基づき、厳格なタスク選択ロジックを実行します（ADR-015）。

### 動作原理

1.  **最高優先度の特定:**
    システムは、処理可能なすべてのタスクの中から、最も数値が小さい（優先度が高い）ラベルを一つだけ特定します。

2.  **タスクのフィルタリング:**
    特定された最高優先度のラベルを持つタスク群のみが、そのサイクルの処理対象となります。

### 具体例

-   リポジトリに `P0` のタスクと `P1` のタスクが存在する場合、`P0` が最高優先度として特定され、**`P0`のタスクのみが処理対象となります**。`P1` のタスクは、`P0`のタスクがすべて無くなるまで処理されません。
-   `P0`も`P1`もなく、`P2`が最も高い優先度である場合は、`P2`のタスク群が処理対象となります。

この「厳格な優先度バケット」の仕組みにより、常に最も重要なタスクから順番に処理されることが保証されます。
```

## 完了条件 (Acceptance Criteria)
- `docs/specs/priority-labels.md` に、上記の「具体的な修正内容」が追記されていること。

## 成果物 (Deliverables)
- 更新された `docs/specs/priority-labels.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/update-priority-labels-doc`
