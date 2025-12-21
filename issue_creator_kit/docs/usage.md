# CLI利用ガイド

このドキュメントは、`issue_creator_kit`に含まれるコマンドラインインターフェース（CLI）の詳細な利用方法について説明します。

## 1. 検証CLI (`validation_cli.py`)

`_in_box`内の計画ファイルが、Issueとして起票できる正しいフォーマットに準拠しているかを検証します。

### コマンド

```bash
python -m issue_creator_kit.interface.validation_cli [OPTIONS]
```

または、パッケージインストール後は以下のコマンドも利用可能です:

```bash
doc-validator [OPTIONS]
```

### オプション

-   **`--repo <owner>/<repo_name>`**:
    (任意) GitHubリポジトリを指定します。指定すると、Issueのラベルがリポジトリに存在するかどうかの検証も行います。
    -   例: `python -m issue_creator_kit.interface.validation_cli --repo masa-codehub/github_broker`

## 2. Issue作成CLI (`cli.py`)

検証済みの計画ファイルに基づき、実際にGitHubリポジトリにIssueを作成します。

### コマンド

```bash
python -m issue_creator_kit.interface.cli [OPTIONS]
```

または、パッケージインストール後は以下のコマンドも利用可能です:

```bash
issue-creator [OPTIONS]
```

### オプション

-   **`--owner <owner_name>`**:
    (必須) Issueを作成するリポジトリのオーナー名（ユーザーまたは組織名）を指定します。
-   **`--repo <repo_name>`**:
    (必須) Issueを作成するリポジトリ名を指定します。
-   **`--path <directory_path>`**:
    (任意) 計画ファイルが格納されているディレクトリのパスを指定します。
    -   デフォルト: `_in_box`
-   **`--dry-run`**:
    (任意) このフラグを立てると、Issue作成の全プロセスを実行しますが、実際にGitHub APIを呼び出してIssueを作成することはありません。コンソールに出力されるログで、どのようなIssueが作成されるかを確認するために使用します。
    -   例: `python -m issue_creator_kit.interface.cli --owner masa-codehub --repo github_broker --dry-run`
-   **`--log-level <LEVEL>`**:
    (任意) ログレベルを指定します。`DEBUG`, `INFO`, `WARNING`, `ERROR` から選択できます。
    -   デフォルト: `INFO`

### 実行例

```bash
# masa-codehub/github_broker リポジトリに実際にIssueを作成する
python -m issue_creator_kit.interface.cli --owner masa-codehub --repo github_broker
```