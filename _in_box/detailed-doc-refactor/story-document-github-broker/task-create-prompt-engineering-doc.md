---
title: "【Task】プロンプトエンジニアリング設計書 `PROMPT_ENGINEERING.md` を新規作成"
labels: ["task", "documentation", "refactoring", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】プロンプトエンジニアリング設計書 `PROMPT_ENGINEERING.md` を新規作成

## 親Issue (Parent Issue)
- (Story: `github_broker`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (なし)

## As-is (現状)
- `GeminiExecutor`がどのようにプロンプトを構築しているか、その設計思想やテンプレートの仕様を解説したドキュメントが存在しない。
- プロンプトの改善や新しい種類のプロンプトの追加を行いたい場合、コードを直接解析する必要があり、属人性が非常に高い。

## To-be (あるべき姿)
- `docs/architecture/PROMPT_ENGINEERING.md`が新規作成される。
- このドキュメントには、プロンプト設計の基本方針、`prompts/`配下のYAMLテンプレートの構造、変数の埋め込みルール、そして新しいプロンプトを追加する際の手順が明確に記述されている。

## ユーザーの意図と背景の明確化
- ユーザーは、AIの挙動を決定するプロンプトを、アドホックな文字列ではなく、管理・拡張可能な「設計」として扱いたいと考えている。プロンプトの品質と再利用性を向上させ、誰でも安全に改善できるようにすることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `docs/architecture/PROMPT_ENGINEERING.md` (新規作成)
- **修正方法:** 以下の内容でファイルを**新規作成**する。

```markdown
# プロンプトエンジニアリング設計書

このドキュメントは、`github_broker`におけるプロンプトの設計思想、テンプレートの仕様、および拡張方法について説明します。

## 1. 基本方針

本プロジェクトにおけるプロンプトは、LLM（Google Gemini）に対して、タスクの背景、目的、そして具体的な成果物の形式を明確に指示することを目的とします。以下の基本方針に基づき設計されています。

-   **役割の付与 (Role-Play):** プロンプトの冒頭で、LLMに「あなたは優秀な〇〇エンジニアです」といった役割を与えることで、出力の専門性と品質を向上させます。
-   **コンテキストの提供:** 関連するIssueのタイトルや本文、ブランチ名などを変数として埋め込み、タスクの背景情報を十分に提供します。
-   **明確な指示:** 「以下のファイルを作成してください」「以下のコードを修正してください」など、実行すべきアクションを明確に指示します。
-   **出力形式の指定:** コードブロックの言語指定（例: ` ```python `）など、期待する出力のフォーマットを厳密に指定します。

## 2. プロンプトテンプレートの仕様

プロンプトは、再利用性と管理性を高めるため、`github_broker/infrastructure/prompts/` ディレクトリ配下にYAML形式のテンプレートとして定義されています。

### テンプレートの構造

各テンプレートは、複数のセクション（キー）から構成されるYAMLオブジェクトです。`GeminiExecutor`はこれらのセクションを結合して、最終的なプロンプトを構築します。

**例: `gemini_executor.yml`**
```yaml
role_play: "あなたは、シニアソフトウェアエンジニアです。"
mission: "以下のタスクを実行してください。"
task_format: |
  # タスク情報
  - Issue URL: {issue_url}
  - ブランチ名: {branch_name}
  - タイトル: {title}
  - 本文:
  {body}
instruction: "上記のタスク情報に基づき、成果物を作成してください。"
```

### 変数の埋め込み

-   テンプレート内の `{variable_name}` という形式の文字列は、`GeminiExecutor`によって実行時に具体的な値に置換されます。
-   利用可能な変数は、`build_prompt`や`build_code_review_prompt`メソッドの引数として渡される`Task`オブジェクトやその他の情報に依存します。
    -   例: `{issue_url}`, `{title}`, `{body}`, `{branch_name}`, `{review_comments}` など。

## 3. 主要なプロンプト

### 3.1. 開発タスク (`gemini_executor.yml`)

-   **目的:** 新規機能の実装やバグ修正など、一般的な開発タスクのコードを生成させる。
-   **利用される主な変数:** `issue_url`, `title`, `body`, `branch_name`

### 3.2. レビュー修正タスク (`review_fix_prompt.yml`)

-   **目的:** 人間のレビューコメントに基づき、既存のコードを修正させる。
-   **利用される主な変数:** `issue_url`, `branch_name`, `file_content`, `review_comments`

## 4. プロンプトの拡張ガイドライン

新しい種類のタスク（例: ドキュメント生成タスク）に対応するプロンプトを追加する際は、以下の手順に従います。

1.  **テンプレートの作成:**
    `github_broker/infrastructure/prompts/` に、新しいYAMLテンプレート（例: `doc_generation_prompt.yml`）を作成します。
2.  **Executorメソッドの追加:**
    `GeminiExecutor`に、新しいテンプレートを読み込み、必要な変数を埋め込むための新しいメソッド（例: `build_doc_generation_prompt`）を追加します。
3.  **Task Serviceの修正:**
    `TaskService`内でタスク種別を判断し、新しく作成したExecutorのメソッドを呼び出すようにロジックを分岐させます。
```

## 完了条件 (Acceptance Criteria)
- `docs/architecture/PROMPT_ENGINEERING.md` が、上記の「具体的な修正内容」で新規作成されていること。

## 成果物 (Deliverables)
- 新規作成された `docs/architecture/PROMPT_ENGINEERING.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/create-prompt-engineering-doc`
