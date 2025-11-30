---
title: "【Task】`issue_creator_kit/README.md`を新規作成"
labels: ["task", "documentation", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】`issue_creator_kit/README.md`を新規作成

## 親Issue (Parent Issue)
- (Story: `issue_creator_kit`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (なし)

## As-is (現状)
- `issue_creator_kit`ディレクトリ直下に、コンポーネントの概要、目的、使い方を説明する`README.md`が存在しない。
- 開発者がこのツールを使おうとしても、何から手をつければ良いか分からない。

## To-be (あるべき姿)
- `issue_creator_kit/README.md`が新規作成される。
- `README.md`には、このツールが何をするためのものか（目的）、インストール方法、最も基本的な実行コマンドが簡潔に記述されており、開発者が即座にツールを試せる状態になる。

## ユーザーの意図と背景の明確化
- ユーザーは、`issue_creator_kit`を他のプロジェクトでも再利用できるような、自己完結したコンポーネントとして扱いたいと考えている。その第一歩として、コンポーネントの入り口となる`README.md`を整備し、ツールの利用方法を明確にすることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `issue_creator_kit/README.md` (新規作成)
- **修正方法:** 以下の内容でファイルを**新規作成**する。

```markdown
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
```

## 完了条件 (Acceptance Criteria)
- `issue_creator_kit/README.md` が、上記の「具体的な修正内容」で新規作成されていること。

## 成果物 (Deliverables)
- 新規作成された `issue_creator_kit/README.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-issue-creator-kit`
- **作業ブランチ (Feature Branch):** `task/create-ick-readme`