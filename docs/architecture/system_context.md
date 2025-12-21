# C4モデル: システムコンテキスト図

## 概要

これは、`github-broker`システム全体のコンテキストをC4モデルのレベル1（システムコンテキスト図）で示したものです。
`github-broker`が、どのユーザーや外部システムと、どのように連携するかを大まかに示します。

## 図

```mermaid
C4Context
  title システムコンテキスト図 for GitHub Broker

  Actor(product_manager, "PRODUCT_MANAGER", "プロジェクトの計画を立案し、\_in\_boxに計画ファイルを作成する。")
  Actor(developer, "Developer", "GitHub上でコードを開発・レビューする人間。")

  System_Ext(github, "GitHub", "ソースコード管理、Issue追跡、Pull Request、Actionsなど。")

  System_Boundary(c1, "GitHub Broker System") {
    System(issue_creator_kit, "Issue Creator Kit", "CLIツール。\_in\_boxの計画ファイルを読み取り、Issueを生成する。")
    System(github_broker, "GitHub Broker", "コアシステム。GitHubを監視し、タスクをエージェントに割り当てる。")
  }

  System_Ext(gemini, "Google Gemini", "Googleが提供するLLM。プロンプトに基づき、コード生成やレビューを行う。")

  Rel(product_manager, issue_creator_kit, "\_in\_box ディレクトリを介して計画を渡す")
  Rel(issue_creator_kit, github, "Issueとブランチを作成する", "GitHub API")

  Rel(developer, github, "コードのPush、PRの作成、レビューを行う")
  Rel(github_broker, github, "IssueとPRの情報をポーリングする", "GitHub API")
  Rel(github, github_broker, "Webhookでイベントを通知する (将来的な拡張)")

  Rel(github_broker, gemini, "プロンプトを送信し、結果を受け取る", "Gemini API")

  UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

## 登場人物とシステム

### アクター (Actors)

-   **PRODUCT_MANAGER:**
    プロジェクト全体の計画を立案し、その結果を`_in_box`ディレクトリ配下にMarkdown形式の計画ファイルとして配置する役割を担うエージェントまたは人間。
-   **Developer:**
    GitHub上で実際にソースコードを記述し、Pull Requestを作成・レビューする人間の開発者。

### システム (Systems)

-   **Issue Creator Kit:**
    `PRODUCT_MANAGER`によって作成された計画ファイルを読み込み、内容を検証し、GitHub APIを介してリポジトリにIssueとブランチを自動で作成する CLI ツール。`github-broker`システムへの主要な入力源です。

-   **GitHub Broker:**
    本プロジェクトのコアシステム。GitHubリポジトリを定期的にポーリングし、新しいIssueやレビュー依頼を検出します。Architecture Decision Record（ADR; アーキテクチャ上の意思決定記録。参考: https://adr.github.io/ ）に基づくビジネスロジック（優先度判定など）に従って最適なタスクを選択し、`Gemini`エージェントに処理を依頼します。

### 外部システム (External Systems)

-   **GitHub:**
    ソースコード、Issue、Pull Requestなどを管理する外部プラットフォーム。`github-broker` はAPI経由で情報を取得し、操作します。
-   **Google Gemini:**
    タスクの実行（コード生成、レビューなど）を担当する外部のLLM。`github-broker`は、状況に応じたプロンプトを生成してGeminiに処理を依頼します。
