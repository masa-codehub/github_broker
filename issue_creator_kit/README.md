# Issue Creator Kit

## 概要

Issue Creator Kitは、`_in_box`ディレクトリに配置されたMarkdown形式の計画ファイル（Epic, Story, Task）を解析・検証し、GitHubリポジトリにIssueとして自動起票するためのコマンドラインツール（CLI）です。

このツールにより、人間が手動でIssueを作成する手間を省き、計画に基づいた正確なIssue作成を自動化します。

## 主な機能

-   Markdownファイルのフロントマターと本文の構造を検証
-   Epic-Story-Taskの親子関係を解析
-   GitHub APIを介したIssueおよびブランチの作成
-   Issue間の親子関係（Sub-issues）の設定

## インストール

プロジェクトのルートディレクトリで、Poetryを使用してインストールします。

```
# 仮想環境に入った後
pip install -e ./issue_creator_kit
```

## 基本的な使い方

### 1. 計画ファイルの検証

Issueを作成する前に、計画ファイルが正しいフォーマットに準拠しているかを検証します。

```bash
doc-validator path/to/your/document.md
```

### 2. Issueの作成

検証済みの計画ファイルから、実際にGitHub Issueを作成します。
このコマンドは、環境変数 `GITHUB_TOKEN`, `GITHUB_REPOSITORY`, `PR_NUMBER` が設定されていることを前提としています。

```bash
# 環境変数を設定して実行する例
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPOSITORY="owner/repo"
export PR_NUMBER="123"

issue-creator
```

詳細なコマンドオプションについては、`docs/usage.md`を参照してください。
