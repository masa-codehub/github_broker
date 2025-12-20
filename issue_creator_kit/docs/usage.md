# CLI利用ガイド

このドキュメントは、`issue_creator_kit`に含まれるコマンドラインインターフェース（CLI）の詳細な利用方法について説明します。

## 1. 検証CLI (`doc-validator`)

`_in_box`内の計画ファイルが、Issueとして起票できる正しいフォーマットに準拠しているかを検証します。

### コマンド

```bash
doc-validator [FILES...]
```

### 引数

-   **`FILES`**:
    (必須) 検証するファイルのパス（複数指定可）。
    -   例: `doc-validator _in_box/my-plan.md`

## 2. Issue作成CLI (`issue-creator`)

検証済みの計画ファイルに基づき、実際にGitHubリポジトリにIssueを作成します。
このコマンドはプルリクエストのコンテキストで実行されることを想定しています。

### コマンド

```bash
issue-creator [OPTIONS]
```

### オプション

-   **`--token <token>`**:
    (任意) GitHubトークン。指定しない場合は環境変数 `GITHUB_TOKEN` が使用されます。
-   **`--repo <repo_name>`**:
    (任意) リポジトリ名（`owner/repo`形式）。指定しない場合は環境変数 `GITHUB_REPOSITORY` が使用されます。

### 必要な環境変数

-   **`PR_NUMBER`**:
    (必須) 対象のプルリクエスト番号。

### 実行例

```bash
export GITHUB_TOKEN="xxx"
export GITHUB_REPOSITORY="owner/repo"
export PR_NUMBER="123"
issue-creator
```
