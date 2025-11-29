---
title: "【Task】`issue_creator_kit/docs/usage.md`を新規作成"
labels: ["task", "documentation", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】`issue_creator_kit/docs/usage.md`を新規作成

## 親Issue (Parent Issue)
- (Story: `issue_creator_kit`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (なし)

## As-is (現状)
- `issue_creator_kit`のCLIツール (`cli.py`, `validation_cli.py`) に実装されているコマンドライン引数（オプション）について、その目的や使い方を説明するドキュメントが存在しない。

## To-be (あるべき姿)
- `issue_creator_kit/docs/usage.md`が新規作成される。
- このドキュメントには、各CLIスクリプトで利用可能な全てのコマンドライン引数について、その意味、デフォルト値、使用例が明確に記述されている。

## ユーザーの意図と背景の明確化
- ユーザーは、CLIツールのインターフェースが明確にドキュメント化されている状態を求めている。これにより、開発者がツールを柔軟かつ正確に利用できるようになり、CI/CDパイプラインへの組み込みなども容易になることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `issue_creator_kit/docs/usage.md` (新規作成)
- **修正方法:** 以下の内容でファイルを**新規作成**する。

```markdown
# CLI利用ガイド

このドキュメントは、`issue_creator_kit`に含まれるコマンドラインインターフェース（CLI）の詳細な利用方法について説明します。

## 1. 検証CLI (`validation_cli.py`)

`_in_box`内の計画ファイルが、Issueとして起票できる正しいフォーマットに準拠しているかを検証します。

### コマンド

```bash
python -m issue_creator_kit.interface.validation_cli [OPTIONS]
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
```

## 完了条件 (Acceptance Criteria)
- `issue_creator_kit/docs/usage.md` が、上記の「具体的な修正内容」で新規作成されていること。

## 成果物 (Deliverables)
- 新規作成された `issue_creator_kit/docs/usage.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-issue-creator-kit`
- **作業ブランチ (Feature Branch):** `task/create-ick-usage-doc`
