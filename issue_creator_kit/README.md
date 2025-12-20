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

```bash
# 仮想環境に入った後
pip install -e ./issue_creator_kit
```

## 基本的な使い方

### 1. 計画ファイルの検証

Issueを作成する前に、計画ファイルが正しいフォーマットに準拠しているかを検証します。

```bash
python -m issue_creator_kit.interface.validation_cli
```

### 2. Issueの作成

検証済みの計画ファイルから、実際にGitHub Issueを作成します。

```bash
# ドライランモードで実行（実際にはIssueを作成しない）
python -m issue_creator_kit.interface.cli --dry-run

# 実際にIssueを作成
python -m issue_creator_kit.interface.cli
```

詳細なコマンドオプションについては、`docs/usage.md`を参照してください。