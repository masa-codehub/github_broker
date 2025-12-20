# データモデル定義書 (`issue_creator_kit`)

このドキュメントは、`issue_creator_kit`のドメイン層で定義・利用される主要なデータモデルについて説明します。

## ドメインモデル

### `DocumentType`

-   **定義場所:** `issue_creator_kit/domain/document.py`
-   **責務:** ドキュメントの種類を識別する列挙型です。バリデーション時のヘッダー定義のキーとして使用されます。
-   **メンバー:**
    -   `ADR`
    -   `DESIGN_DOC`
    -   `PLAN`
    -   `IN_BOX`

### `IssueData`

-   **定義場所:** `issue_creator_kit/domain/issue.py`
-   **責務:** GitHubに起票されるIssueのデータを保持するデータクラスです。ファイルコンテンツのYAML Front Matterと本文から生成されます。
-   **主要プロパティ:**
    -   `title`: `str` - Issueのタイトル。
    -   `body`: `str` - Issueの本文（Markdown形式）。
    -   `labels`: `list[str]` - Issueに付与されるラベルのリスト。
    -   `assignees`: `list[str]` - アサイン先ユーザー名のリスト。

## モデル間の関係とデータフロー

ツールの主要なデータフローは、`_in_box`内のファイルから`IssueData`への変換、そしてGitHub Issueの作成です。

```mermaid
graph TD
    A["_in_box内のファイル"] -->|GithubServiceが取得| B(ファイルコンテンツ str);
    B -->|parse_issue_content| C[IssueData オブジェクト];
    C -->|IssueCreationServiceが利用| D(GithubService.create_issue);
    D -->|PyGithubを利用| E[GitHub API (Issue作成)];
    D -->|成功時| F[_done_boxへ移動];
    D -->|失敗時| G[_failed_boxへ移動];
```

1.  `IssueCreationService`が`GithubService`を使用して`_in_box`ディレクトリ内のファイルを取得します。
2.  各ファイルの内容（文字列）は、`parse_issue_content`関数によって解析されます。
    - YAML Front Matterから`title`, `labels`, `assignees`を抽出します。
    - 残りの部分を`body`として抽出します。
3.  解析結果は`IssueData`オブジェクトとしてインスタンス化されます。
4.  `IssueCreationService`は`IssueData`の情報を用いて`GithubService.create_issue`を呼び出し、GitHub Issueを作成します。
5.  処理結果に応じて、ファイルは`_done_box`または`_failed_box`に移動されます。