# ファイル発見と階層構造のルール

このドキュメントは、`issue_creator_kit`が`_in_box`ディレクトリから計画ファイルをどのように発見し、それらの親子関係をどのように決定するかのルールについて説明します。

## 1. ファイル発見のルール

-   ファイルシステムを操作するコンポーネントは、`_in_box`ディレクトリ配下を再帰的に探索し、`.md`拡張子を持つ全てのファイルを収集します。
-   `.gitkeep`などの隠しファイルや、`.md`以外の拡張子を持つファイルは無視されます。

## 2. 階層構造とIssueタイプの判定ロジック

Issueのタイプ（Epic/Story/Task）はファイルの**Frontmatter内のラベル**によって決定され、親子関係は**ディレクトリパス**に基づいて推論されます。

### Issueタイプの判定 (Labels)

各`.md`ファイルは、Frontmatterの `labels` フィールドに `epic`, `story`, `task` のいずれかを含める必要があります。

-   **Epic:** `labels` に `epic` を含むファイル。
-   **Story:** `labels` に `story` を含むファイル。
-   **Task:** `labels` に `task` を含むファイル。

### 親子関係の推論 (Directory Structure)

ディレクトリ構造に基づいて、以下のように親子関係が推論されます。

-   **Epic:** `_in_box/` 直下のディレクトリに対応します。
-   **Story:** Epicディレクトリ直下のサブディレクトリに対応し、親はそのEpicとなります。
-   **Task:** Storyディレクトリ配下のファイルに対応し、親はそのStoryとなります。

**注意:** 同一ディレクトリ内にStory定義ファイル（`label: story`）とTaskファイル（`label: task`）が混在する場合、ラベルによって明確に区別されます。

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
