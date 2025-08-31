# Capability Taxonomy

このドキュメントは、本プロジェクトで利用するエージェントの能力（Capability）およびIssueで要求されるスキルの標準的な語彙体系を定義します。Issueを作成する際は、ここで定義されたキーワードを`must:`または`want:`のプレフィックスと共に使用してください。

これはリビングドキュメントであり、プロジェクトの進捗に応じて更新されます。

---

## 1. 能力（Capability）の語彙体系

### カテゴリー

#### 1.1. プログラミング言語 (Programming Languages)
- `python`
- `shell`
- `typescript`

#### 1.2. フレームワーク & ライブラリ (Frameworks & Libraries)
- `fastapi`
- `pydantic`
- `pytest`
- `react`
- `sqlalchemy`

#### 1.3. ツール & プラットフォーム (Tools & Platforms)
- `aws`
- `docker`
- `gcp`
- `git`
- `github-actions`
- `redis`

#### 1.4. スキル & 概念 (Skills & Concepts)
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

---

## 2. エージェントの役割と必須スキル

各エージェントの役割と、その役割を遂行する上で最低限必要となる必須スキル（must-have skills）の対応表です。

| エージェント名 | 必須スキル（`must`） |
| :--- | :--- |
| **BACKEND_CODER** | `python`, `fastapi`, `pydantic`, `pytest`, `git`, `docker`, `api-design`, `test-writing` |
| **FRONT_END_CODER** | `typescript`, `react`, `git`, `docker`, `ui-design` |
| **SYSTEM_ARCHITECT** | `architecture-design`, `api-design`, `security`, `performance`, `docker` |
| **UIUX_DESIGNER** | `ui-design`, `ux-research` |
| **CONTENTS_WRITER** | `documentation`, `copywriting` |
| **MARKET_RESEARCHER** | `web-research`, `documentation` |
| **PEST_ANALYST** | `pest-analysis`, `documentation` |
| **STRATEGIST** | `strategy-planning`, `issue-analysis` |