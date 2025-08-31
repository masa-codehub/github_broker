# Capability Taxonomy

このドキュメントは、本プロジェクトで利用するエージェントの能力（Capability）およびIssueで要求されるスキルの標準的な語彙体系を定義します。Issueを作成する際は、ここで定義されたキーワードを`must:`または`want:`のプレフィックスと共に使用してください。

これはリビングドキュメントであり、プロジェクトの進捗に応じて更新されます。

---

## 1. 共通スキル (Core Skills)

役割を問わず、ほとんどのエージェントが持つべき基本的な能力です。個別のエージェントの必須スキルリストでは、これらの記載を省略することがあります。

- `git`: バージョン管理の基本操作
- `documentation`: ドキュメントの読解や、成果物をドキュメントとしてまとめる能力

## 2. 専門エージェントの役割と必須スキル

各エージェントの主な役割と、その役割を遂行する上で専門的に要求される必須スキル（`must`スキル）を定義します。

### 2.1. 開発 (Development)

#### BACKEND_CODER
- **役割:** Pythonを用いたAPIサーバーの設計、実装、テストを担当します。
- **必須スキル:** `python`, `fastapi`, `pydantic`, `pytest`, `api-design`, `test-writing`, `docker`

#### FRONT_END_CODER
- **役割:** TypeScriptとReactを用いたフロントエンドアプリケーションの設計、実装を担当します。
- **必須スキル:** `typescript`, `react`, `ui-design`, `docker`

### 2.2. 設計 (Design)

#### SYSTEM_ARCHITECT
- **役割:** システム全体のアーキテクチャ設計、技術選定、非機能要件（パフォーマンス、セキュリティ）の定義を担当します。
- **必須スキル:** `architecture-design`, `api-design`, `security`, `performance`

#### UIUX_DESIGNER
- **役割:** ユーザー体験（UX）のリサーチと、それに基づいたユーザーインターフェース（UI）の設計を担当します。
- **必須スキル:** `ui-design`, `ux-research`

### 2.3. コンテンツ & 分析 (Contents & Analysis)

#### CONTENTS_WRITER
- **役割:** ドキュメント、ブログ記事、UIのマイクロコピーなど、テキストコンテンツの執筆を担当します。
- **必須スキル:** `copywriting`

#### MARKET_RESEARCHER
- **役割:** ウェブ上の情報収集や競合分析を通じて、市場の動向を調査・報告します。
- **必須スキル:** `web-research`

#### PEST_ANALYST
- **役割:** 政治・経済・社会・技術の観点からマクロ環境を分析し、事業戦略への影響を報告します。
- **必須スキル:** `pest-analysis`

#### STRATEGIST
- **役割:** プロジェクト全体の課題を分析し、次のアクションアイテム（Issue）を起票して戦略を立案します。
- **必須スキル:** `strategy-planning`, `issue-analysis`

---

## 3. 実装との関連 (Mapping to Implementation)

このドキュメントで定義されたルールは、GitHubブローカーのコアロジックに直接反映されています。

- **担当コード:** `github_broker/application/task_service.py`

### 処理フロー

1.  **フィルタリング (Filtering):** `TaskService`は、Issueに付与された`must:`で始まるラベルをすべて抽出し、タスクを要求してきたエージェントがそれらの能力（Capability）を**すべて**持っているか検証します。条件を満たさないIssueは、この時点で候補から除外されます。

2.  **ソーティング (Sorting):** フィルタリングを通過したIssue候補の中から、残りのラベル（`want:`ラベルやプレフィックスなしのラベル）とエージェントの能力が最も多く一致するIssueを最優先タスクとして選択します。
