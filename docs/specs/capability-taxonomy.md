# Capability Taxonomy

このドキュメントは、本プロジェクトで利用するエージェントの能力（Capability）およびIssueで要求されるスキルの標準的な語彙体系を定義します。Issueを作成する際は、ここで定義されたキーワードを`must:`または`want:`のプレフィックスと共に使用してください。

これはリビングドキュメントであり、プロジェクトの進捗に応じて更新されます。

---

## 1. 能力（Capability）の語彙体系

プロジェクト内で使用される標準的なスキルキーワードのマスターリストです。

### 1.1. プログラミング言語
- `python`
- `shell`
- `typescript`

### 1.2. フレームワーク & ライブラリ
- `fastapi`
- `pydantic`
- `pytest`
- `react`
- `sqlalchemy`

### 1.3. ツール & プラットフォーム
- `aws`
- `docker`
- `gcp`
- `git`
- `github-actions`
- `redis`

### 1.4. スキル & 概念
- `api-design`
- `architecture-design`
- `backend`
- `bugfix`
- `ci-cd`
- `copywriting`
- `documentation`
- `frontend`
- `issue-analysis`
- `performance`
- `performance-tuning`
- `pest-analysis`
- `refactor`
- `refactoring`
- `security`
- `strategy-planning`
- `test-writing`
- `ui-design`
- `ux-research`
- `web-research`

### 1.5. プロセス & ステータス
- `code-review`
- `needs-review`

---

## 2. エージェントの役割と必須スキル

### 2.1. 共通必須スキル (Common Must-Have Skills)

開発や分析に関わる多くのエージェントが共通して持つべき必須スキルです。

- `git`: バージョン管理
- `docker`: コンテナ技術
- `documentation`: ドキュメントの読解・作成

### 2.2. 専門スキル (Specialized Skills)

各エージェントの役割と、共通スキルに加えて要求される専門的な必須スキル（`must`スキル）の対応表です。

| エージェント名 | 役割 | 専門必須スキル（`must`） |
| :--- | :--- | :--- |
| **BACKEND_CODER** | APIサーバーの設計、実装、テスト | `python`, `fastapi`, `pydantic`, `pytest`, `api-design`, `test-writing` |
| **FRONT_END_CODER** | フロントエンドUIの実装 | `typescript`, `react`, `ui-design` |
| **SYSTEM_ARCHITECT** | システム全体のアーキテクチャ設計 | `architecture-design`, `api-design`, `security`, `performance` |
| **UIUX_DESIGNER** | UI設計とUXリサーチ | `ui-design`, `ux-research` |
| **CODE_REVIEWER** | コードレビューとフィードバック | `code-review`, `needs-review`, `python`, `typescript` |
| **CONTENTS_WRITER** | テキストコンテンツの執筆 | `copywriting` |
| **MARKET_RESEARCHER** | 市場動向の調査・報告 | `web-research` |
| **PEST_ANALYST** | マクロ環境の分析・報告 | `pest-analysis` |
| **STRATEGIST** | 戦略立案と課題起票 | `strategy-planning`, `issue-analysis` |

---

## 3. 実装との関連 (Mapping to Implementation)

このドキュメントで定義されたルールは、GitHubブローカーのコアロジックに直接反映されています。

- **担当コード:** `github_broker/application/task_service.py`

### 処理フロー

1.  **フィルタリング (Filtering):** `TaskService`は、Issueに付与された`must:`で始まるラベルをすべて抽出し、タスクを要求してきたエージェントがそれらの能力（Capability）を**すべて**持っているか検証します。条件を満たさないIssueは、この時点で候補から除外されます。

2.  **ソーティング (Sorting):** フィルタリングを通過したIssue候補の中から、残りのラベル（`want:`ラベルやプレフィックスなしのラベル）とエージェントの能力が最も多く一致するIssueを最優先タスクとして選択します。