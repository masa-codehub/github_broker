# Code Overview (`issue_creator_kit`)

このドキュメントは、`issue_creator_kit`コンポーネントのコードベースにおける各ファイルの機能と役割を説明します。本コンポーネントもクリーンアーキテクチャの原則に基づいています。

## フォルダ構成

```
issue_creator_kit/
├── application/
│   ├── issue_service.py
│   └── validation_service.py
├── domain/
│   ├── document.py
│   └── issue.py
├── infrastructure/
│   ├── file_system_service.py
│   └── github_service.py
└── interface/
    ├── cli.py
    └── validation_cli.py
```

## 各レイヤーの概要とファイル詳細

### 1. Domain Layer

`issue_creator_kit`のコアとなるビジネスルールとエンティティを定義します。

-   **`domain/document.py`**:
    -   **概要:** Markdown計画ファイルそのものを表現するエンティティ。ファイルパス、フロントマター、本文などの情報を保持します。
-   **`domain/issue.py`**:
    -   **概要:** `Document`から生成されるGitHub Issueの情報を表現するエンティティ。Issueのタイトル、本文、ラベルなどを保持します。

### 2. Application Layer

具体的なユースケースを実装します。

-   **`application/validation_service.py`**:
    -   **責務:** `Document`オブジェクトを受け取り、それがIssueとして起票できる正しいフォーマットか（必須セクションの存在、ラベル規約など）を検証します。
    -   **詳細:** 検証ルールは`validation-rules.md`に定義されています。
-   **`application/issue_service.py`**:
    -   **責務:** 検証済みの`Document`群を受け取り、それらを`Issue`オブジェクトに変換し、`GitHubService`を通じて実際にIssueを作成します。Epic-Story-Taskの階層構造を解釈し、親子関係を設定する責務も持ちます。

### 3. Interface Layer

外部（この場合はユーザーやCI/CD環境）とのインターフェースを提供します。

-   **`interface/validation_cli.py`**:
    -   **責務:** `ValidationService`を呼び出すためのCLIエントリーポイント。ユーザーが計画ファイルの検証を手動で実行するために使用します。
-   **`interface/cli.py`**:
    -   **責務:** `IssueService`を呼び出すためのCLIエントリーポイント。`--dry-run`オプションなども処理します。

### 4. Infrastructure Layer

外部の世界（ファイルシステム、GitHub API）との具体的なやり取りを実装します。

-   **`infrastructure/file_system_service.py`**:
    -   **責務:** ローカルのファイルシステムを操作します。`_in_box`ディレクトリから再帰的に`.md`ファイルを探索する責務を持ちます。
-   **`infrastructure/github_service.py`**:
    -   **責務:** `PyGithub`ライブラリを使用し、GitHub APIとの通信を担います。Issueの作成、ブランチの作成、Issueの親子関係設定などを行います。
