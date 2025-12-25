# Issue Creator Kit

`issue_creator_kit` は、Issueの作成、検証、およびワークフロー管理を補助するためのライブラリです。
`github_broker` システムの一部として、またはスタンドアロンのCLIツールとして使用されます。

## 機能

- **Issueファイルの検証**: Markdown形式のIssueファイルが、プロジェクトの規約（必須セクション、ラベル、ブランチ戦略など）に準拠しているかを検証します。
- **自動起票ワークフロー**: `_in_box/` ディレクトリに配置されたMarkdownファイルを解析し、GitHub Issueを自動的に作成します。
- **GitOps連携**: `pre-commit` フックや GitHub Actions と連携し、開発プロセスの一貫性を保ちます。

## ドキュメント

- [バリデーションルール一覧](./validation-rules.md): `.md` ファイルに求められる詳細なフォーマットルール。
- [自動起票ワークフロー (ADR-017)](./adr-017-workflow/index.md): ワークフローの全体像とアーキテクチャ。
- [コード概要](./code-overview.md): ソースコードの構成。

## インストール

```bash
pip install -e issue_creator_kit
```

## CLIとしての使用

`issue_creator_kit` は `validation_cli` というコマンドラインツールを提供します。

```bash
# 特定のファイルを検証
python3 issue_creator_kit/interface/cli.py --file path/to/issue.md

# _in_box ディレクトリ内の全ファイルを検証
python3 issue_creator_kit/interface/cli.py --dir _in_box
```