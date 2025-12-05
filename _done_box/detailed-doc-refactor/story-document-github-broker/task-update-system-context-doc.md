---
title: "【Task】`system_context.md`にIssue Creator Kitを追記"
labels: ["task", "documentation", "refactoring", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】`system_context.md`にIssue Creator Kitを追記

## 親Issue (Parent Issue)
- (Story: `github_broker`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (なし)

## As-is (現状)
- `docs/architecture/system_context.md`のC4モデル図に、`issue_creator_kit`コンポーネントとその役割が含まれていない。
- `github_broker`が処理するIssueが、どのようにしてGitHub上に作成されるのかという、システムの重要な入力プロセスが図から欠落している。

## To-be (あるべき姿)
- `system_context.md`のC4モデル図と説明文が更新され、`PRODUCT_MANAGER`（アクター）と`Issue Creator Kit`（システム）が追加される。
- `PRODUCT_MANAGER` -> `_in_box` -> `Issue Creator Kit` -> `GitHub` -> `Github Broker` という、Issue生成から処理までのエコシステム全体が、図と文章で明確に表現される。

## ユーザーの意図と背景の明確化
- ユーザーは、プロジェクトの全体像を俯瞰するコンテキスト図が、現状の実装と完全に一致している状態を求めている。特に、システムの主要な入力源である`issue_creator_kit`が図に含まれていない点を問題視しており、全体的なデータフローの理解を容易にしたいと考えている。

## **具体的な修正内容**
- **対象ファイル:** `docs/architecture/system_context.md`
- **修正方法:** ファイル全体を以下の内容で**上書き**する。

```markdown
# C4モデル: システムコンテキスト図

## 概要

これは、`github-broker`システム全体のコンテキストをC4モデルのレベル1（システムコンテキスト図）で示したものです。
`github-broker`が、どのユーザーや外部システムと、どのように連携するかを大まかに示します。

## 図

```mermaid
C4Context
  title システムコンテキスト図 for Github Broker

  Actor(product_manager, "PRODUCT_MANAGER", "プロジェクトの計画を立案し、_in_boxに計画ファイルを作成する。")
  Actor(developer, "Developer", "GitHub上でコードを開発・レビューする人間。")

  System_Ext(github, "GitHub", "ソースコード管理、Issue追跡、Pull Request、Actionsなど。")

  System_Boundary(c1, "Github Broker System") {
    System(issue_creator_kit, "Issue Creator Kit", "CLIツール。_in_boxの計画ファイルを読み取り、Issueを生成する。")
    System(github_broker, "Github Broker", "コアシステム。GitHubを監視し、タスクをエージェントに割り当てる。")
  }

  System_Ext(gemini, "Google Gemini", "Googleが提供するLLM。プロンプトに基づき、コード生成やレビューを行う。")

  Rel(product_manager, issue_creator_kit, "_in_box ディレクトリを介して計画を渡す")
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
    `PRODUCT_MANAGER`によって作成された計画ファイルを読み込み、内容を検証し、GitHub APIを介してリポジトリにIssueとブランチを自動で作成するCLIツール。`github-broker`システムへの主要な入力源です。

-   **Github Broker:**
    本プロジェクトのコアシステム。GitHubリポジトリを定期的にポーリングし、新しいIssueやレビュー依頼を検出します。ADRに基づいたビジネスロジック（優先度判定など）に従って最適なタスクを選択し、`Gemini`エージェントに処理を依頼します。

### 外部システム (External Systems)

-   **GitHub:**
    ソースコード、Issue、Pull Requestなどを管理する外部プラットフォーム。`github-broker` はAPI経由で情報を取得し、操作します。
-   **Google Gemini:**
    タスクの実行（コード生成、レビューなど）を担当する外部のLLM。`github-broker`は、状況に応じたプロンプトを生成してGeminiに処理を依頼します。

```

## 完了条件 (Acceptance Criteria)
- `docs/architecture/system_context.md` が、上記の「具体的な修正内容」で上書きされていること。

## 成果物 (Deliverables)
- 更新された `docs/architecture/system_context.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/update-system-context-doc`
