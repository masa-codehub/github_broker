# How to Contribute

このプロジェクトへの貢献に興味を持っていただき、ありがとうございます。このドキュメントは、開発を円滑に進めるための規約やワークフローを定義します。

## 開発環境

開発環境のセットアップについては、`README.md`の「2. 実行方法」を参照してください。

## 開発ワークフロー

本プロジェクトは、複数のAIエージェントが協調して開発を進める、特殊なワークフローを採用しています。

1.  **担当Issueの決定:** 各エージェントは、自身に割り当てられた役割（Role）のラベルが付いたIssueの中から、未着手のものを選択します。
2.  **開発の実施:** Issueの完了条件に従い、`main`ブランチから新しいブランチを作成して開発を行います。
3.  **Pull Requestの作成:** 変更が完了したら、`main`ブランチに対してPull Requestを作成します。PRの本文には、`Closes #<issue番号>`を記載してください。

詳細なワークフローは、`docs/specs/development-workflow.md`を参照してください。

## コーディング規約

- **フォーマッター:** Black
- **リンター:** Ruff

これらのツールは`pyproject.toml`で定義されており、pre-commitフックによって自動的に実行されます。

## コミットメッセージ

コミットメッセージは [Conventional Commits](https://www.conventionalcommits.org/) の規約に準拠してください。

- **フォーマット:** `<type>(<scope>): <subject>`
- **例:**
    - `feat(api): Add agent_role to request model`
    - `docs(workflow): Update development workflow diagram`
    - `fix(service): Correct task assignment logic`

## Issueの起票

- 新しいIssueを作成する際は、必ず担当すべきエージェントの役割ラベル（例: `BACKENDCODER`, `STRATEGIST`）を一つ付与してください。
- Issueのタイトルは、`【P<優先度>/<type>】<内容>` の形式で記述してください。（例: `【P0/feature】役割ベースのタスク割り当てロジックへの全面的な仕様変更`）
