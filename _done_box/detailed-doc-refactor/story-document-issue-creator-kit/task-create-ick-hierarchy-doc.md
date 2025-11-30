---
title: "【Task】`issue_creator_kit`のファイル発見・階層化ルール `file-discovery-and-hierarchy.md` を新規作成"
labels: ["task", "documentation", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】`issue_creator_kit`のファイル発見・階層化ルール `file-discovery-and-hierarchy.md` を新規作成

## 親Issue (Parent Issue)
- (Story: `issue_creator_kit`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (なし)

## As-is (現状)
- `issue_creator_kit`が、`_in_box`内のディレクトリ構造からIssueの親子関係を推論するための、暗黙的なルールについて記述したドキュメントが存在しない。
- `PRODUCT_MANAGER`が、どのようなディレクトリ構造で計画ファイルを作成すれば、意図した通りの親子関係が設定されるのかを知るすべがない。

## To-be (あるべき姿)
- `issue_creator_kit/docs/file-discovery-and-hierarchy.md`が新規作成される。
- このドキュメントには、ツールが`.md`ファイルを探索する際のルールと、ファイルパスからIssueの親子関係を決定するための具体的なロジックが明記されている。

## ユーザーの意図と背景の明確化
- ユーザーは、`PRODUCT_MANAGER`が迷いなく、かつ正確に計画ファイルを作成できる環境を求めている。ツールの暗黙的な前提条件をすべて明文化することで、属人性を排除し、計画作成の効率を向上させることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `issue_creator_kit/docs/file-discovery-and-hierarchy.md` (新規作成)
- **修正方法:** 以下の内容でファイルを**新規作成**する。

```markdown
# ファイル発見と階層構造のルール

このドキュメントは、`issue_creator_kit`が`_in_box`ディレクトリから計画ファイルをどのように発見し、それらの親子関係をどのように決定するかのルールについて説明します。

## 1. ファイル発見のルール

-   `FileSystemService`は、`_in_box`ディレクトリ配下を再帰的に探索し、`.md`拡張子を持つ全てのファイルを収集します。
-   `.gitkeep`などの隠しファイルや、`.md`以外の拡張子を持つファイルは無視されます。

## 2. 階層構造の推論ロジック

Issueの親子関係は、収集された`.md`ファイルの**ディレクトリパス**に基づいて自動的に推論されます。

### 基本ルール

-   **Epic:** `_in_box/`の直下にあるディレクトリが、それぞれ一つのEpicに対応します。Epic自身の定義ファイルは、そのディレクトリ直下の`.md`ファイルです。
-   **Story:** Epicディレクトリの直下にあるサブディレクトリが、Storyに対応します。Story自身の定義ファイルは、そのサブディレクトリ直下の`.md`ファイルです。
-   **Task:** Storyディレクトリの配下にある`.md`ファイルが、Taskに対応します。

### 具体的なディレクトリ構造の例

以下のディレクトリ構造は、ツールによって正しく解釈される親子関係の例です。

```
_in_box/
└── epic-A/  (Epic A)
    ├── epic-A.md
    ├── story-B/  (Story B, Parent: Epic A)
    │   ├── story-B.md
    │   ├── task-C.md  (Task C, Parent: Story B)
    │   └── task-D.md  (Task D, Parent: Story B)
    │
    └── story-E/  (Story E, Parent: Epic A)
        ├── story-E.md
        └── sub-story/ (注: この階層は推奨されません)
            └── task-F.md (Task F, Parent: Story E)
```

### 注意事項

-   **ファイル名:** ファイル名はIssueの親子関係に影響を与えませんが、混乱を避けるため、定義するIssueの内容と一致させることが推奨されます（例: `epic-A`ディレクトリ内のEpic定義ファイルは`epic-A.md`とする）。
-   **階層の深さ:** ツールは深い階層も解析しますが、原則として`Epic -> Story -> Task`の3階層で管理することが推奨されます。Story配下にさらにサブディレクトリを作成することも可能ですが、意図しない親子関係が生まれる可能性があるため注意が必要です。
-   **単一の定義ファイル:** 各EpicおよびStoryディレクトリには、その本体を定義する`.md`ファイルが一つだけ含まれていることを想定しています。

```

## 完了条件 (Acceptance Criteria)
- `issue_creator_kit/docs/file-discovery-and-hierarchy.md` が、上記の「具体的な修正内容」で新規作成されていること。

## 成果物 (Deliverables)
- 新規作成された `issue_creator_kit/docs/file-discovery-and-hierarchy.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-issue-creator-kit`
- **作業ブランチ (Feature Branch):** `task/create-ick-hierarchy-doc`
