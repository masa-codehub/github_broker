# 貢献方法

このプロジェクトへの貢献に興味を持っていただき、ありがとうございます。このドキュメントは、開発を円滑に進めるための規約やワークフローを定義します。

## 開発環境

### 1. .envファイルの準備

プロジェクトのルートディレクトリに`.env`ファイルを作成し、`.build/context/.env.sample`を参考に、実行環境に合わせて必要な環境変数を設定してください。

### 2. 機密情報の設定 (Docker Secrets)

本番環境ではDocker Secretsを利用して機密情報を安全に扱います。ローカル開発環境では、以下の手順で同様の仕組みを再現します。

1.  プロジェクトのルートディレクトリに`secrets`という名前のディレクトリを作成します。
    ```bash
    mkdir secrets
    ```

2.  `secrets`ディレクトリ内に、以下のファイル名でそれぞれの機密情報を記述したファイルを作成します。
    -   `github_token`: ご自身のGitHub Personal Access Tokenを記述します。
    -   `gemini_api_key`: ご自身のGemini APIキーを記述します。

    **（注意）`secrets`ディレクトリとその中のファイルは、Gitの追跡対象外（`.gitignore`に記載済み）です。**

### 3. コンテナのビルドと実行

上記の設定が完了したら、`docker-compose`コマンドでコンテナをビルドし、起動します。

```bash
docker-compose up --build -d
```


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
    - `feat(api): Add agent_role to request model` (apiスコープの機能追加)
    - `docs(workflow): Update development workflow diagram` (workflowスコープのドキュメント更新)
    - `fix(service): Correct task assignment logic` (serviceスコープのバグ修正)

## Issueの起票

- 新しいIssueを作成する際は、必ず担当すべきエージェントの役割ラベル（例: `BACKENDCODER`, `STRATEGIST`）を一つ付与してください。
- Issueのタイトルは、`【P<優先度>/<type>】<内容>` の形式で記述してください。（例: `【P0/feature】役割ベースのタスク割り当てロジックへの全面的な仕様変更`）

### `<type>`の種類

- **feat:** 新機能の追加
- **fix:** バグ修正
- **docs:** ドキュメントのみの変更
- **style:** コードの動作に影響しない、スタイルに関する変更（スペース、フォーマットなど）
- **refactor:** バグ修正でも機能追加でもない、コードのリファクタリング
- **test:** 不足しているテストの追加や、既存テストの修正
- **chore:** ビルドプロセスや補助ツール、ライブラリの変更など（ソースコードの変更を含まない）
- **epic:** エピック（大規模な機能や目標）に関連する変更
- **story:** ストーリー（ユーザーの要求や機能）に関連する変更

### `<優先度>`の種類

- **P0:** 開発の前提となる最重要課題
- **P1:** 中核機能の開発
- **P2:** 戦略・技術調査
- **P3:** 高度な機能とUI/UXの改善
- **P4:** 本番化に向けた準備