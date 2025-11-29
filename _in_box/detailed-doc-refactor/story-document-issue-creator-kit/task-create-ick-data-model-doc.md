---
title: "【Task】`issue_creator_kit`のデータモデル定義書 `data-model.md` を新規作成"
labels: ["task", "documentation", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】`issue_creator_kit`のデータモデル定義書 `data-model.md` を新規作成

## 親Issue (Parent Issue)
- (Story: `issue_creator_kit`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (なし)

## As-is (現状)
- `issue_creator_kit`のドメインの中心となる`Document`モデルと`Issue`モデルについて、その役割や関係性を解説したドキュメントが存在しない。

## To-be (あるべき姿)
- `issue_creator_kit/docs/data-model.md`が新規作成される。
- このドキュメントには、`Document`と`Issue`の各モデルの責務、主要なプロパティ、そして`Document`から`Issue`への変換プロセスが簡潔に記述されている。

## ユーザーの意図と背景の明確化
- ユーザーは、ツールの中心的なデータ構造を明確にドキュメント化することで、ロジックの理解を容易にし、将来の機能拡張（例: 新しいフロントマター項目の追加）を安全に行えるようにしたいと考えている。

## **具体的な修正内容**
- **対象ファイル:** `issue_creator_kit/docs/data-model.md` (新規作成)
- **修正方法:** 以下の内容でファイルを**新規作成**する。

```markdown
# データモデル定義書 (`issue_creator_kit`)

このドキュメントは、`issue_creator_kit`のドメイン層で定義・利用される主要なデータモデルについて説明します。

## ドメインモデル

### `Document`

-   **定義場所:** `issue_creator_kit/domain/document.py`
-   **責務:** `_in_box`に配置された単一のMarkdown計画ファイル（`.md`）を表現するドメインエンティティです。このモデルは、ファイルの内容を構造化データとして保持し、検証の対象となります。
-   **主要プロパティ:**
    -   `path`: `Path` - ファイルへのパス。
    -   `front_matter`: `dict` - YAMLフロントマターをパースした辞書。
    -   `content`: `str` - Markdownの本文。
    -   `issue_type`: `IssueType` (Enum) - `epic`, `story`, `task` のいずれか。
    -   `parent_path`: `Path | None` - 親となる計画ファイルのパス。階層構造の解析に使用されます。

### `Issue`

-   **定義場所:** `issue_creator_kit/domain/issue.py`
-   **責務:** `Document`モデルから変換された、GitHubに起票されるべき単一のIssueの情報を表現するドメインエンティティです。
-   **主要プロパティ:**
    -   `title`: `str` - Issueのタイトル。
    -   `body`: `str` - Issueの本文。
    -   `labels`: `list[str]` - Issueに付与されるラベル。
    -   `issue_type`: `IssueType` (Enum)
    -   `parent`: `Issue | None` - 親Issueへの参照。

## モデル間の関係とデータフロー

ツールの主要なデータフローは、`Document`から`Issue`への変換です。

```mermaid
graph TD
    A["`_in_box`内の.mdファイル"] -->|`FileSystemService`が読み込み| B(Document オブジェクト);
    B -->|`ValidationService`が検証| C{検証OK?};
    C -- Yes --> D[Issue オブジェクト];
    C -- No --> E[エラー出力];
    D -->|`IssueService`が処理| F(GitHubService);
    F -->|`PyGithub`を利用| G[GitHub API];
```

1.  `FileSystemService`が`_in_box`から`.md`ファイルを探索し、それぞれを`Document`オブジェクトとしてインスタンス化します。
2.  `ValidationService`が各`Document`オブジェクトを検証します。
3.  `IssueService`が検証済みの`Document`オブジェクトを受け取り、`Issue`オブジェクトへと変換します。この際、親子関係も解決されます。
4.  最終的に、`IssueService`は`GitHubService`を呼び出し、`Issue`オブジェクトの情報に基づいてGitHub API経由で実際のIssueを作成します。
```

## 完了条件 (Acceptance Criteria)
- `issue_creator_kit/docs/data-model.md` が、上記の「具体的な修正内容」で新規作成されていること。

## 成果物 (Deliverables)
- 新規作成された `issue_creator_kit/docs/data-model.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-issue-creator-kit`
- **作業ブランチ (Feature Branch):** `task/create-ick-data-model-doc`
