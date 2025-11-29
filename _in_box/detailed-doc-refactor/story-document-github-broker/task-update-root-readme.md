---
title: "【Task】ルート`README.md`を新しいドキュメント構造とコンポーネント構成に更新"
labels: ["task", "documentation", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】ルート`README.md`を新しいドキュメント構造とコンポーネント構成に更新

## 親Issue (Parent Issue)
- (Story: `github_broker`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (なし)

## As-is (現状)
- プロジェクトルートの`README.md`が、古いドキュメント構造へのリンクを含んでいる。
- `github_broker`と`issue_creator_kit`という2つの主要コンポーネントが同居しているリポジトリ構造についての説明が欠けている。

## To-be (あるべき姿)
- `README.md`のドキュメントへのリンクが、`docs/architecture/`や`reqs/`といった新しい構造を指すように更新される。
- 「リポジトリ構造」セクションが追加され、`github_broker`（コアエンジン）と`issue_creator_kit`（Issue生成CLI）の役割分担が明確に説明される。
- 新規参画者が`README.md`を読むだけで、プロジェクトの全体像と主要なドキュメントへの正しい入り口を把握できる。

## ユーザーの意図と背景の明確化
- ユーザーは、プロジェクトの「顔」である`README.md`が、常に正確で最新の情報を提供することを求めている。ドキュメント構成のリファクタリングが完了した際に、`README.md`がハブとして正しく機能し、開発者を適切な情報へ誘導できるようにすることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `README.md`
- **修正方法:** ファイル全体を以下の内容で**上書き**する。

```markdown
# GitHub Broker

[![CI](https://github.com/masa-codehub/github_broker/actions/workflows/ci.yml/badge.svg)](https://github.com/masa-codehub/github_broker/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**人間とAIの対話を通じてプロダクト開発を駆動させる、自律型AIエージェントチームのためのフレームワーク**

---

## コンセプト

GitHub Brokerは、人間とAI（特にPRODUCT_MANAGERエージェント）との戦略的な対話を通じて、開発の方向性を決定し、具体的なIssueを生成します。そして、そのIssueに基づき、自律的なAI開発エージェントチームが設計、実装、テストを自動で実行する、新しいプロダクト開発の形を実現するためのフレームワークです。

## プロジェクトのビジョン

私たちは、**人間とAIの協調による、高速で自律的な開発サイクル**の実現を目指しています。

人間はより創造的で戦略的な意思決定に集中し、AIは具体的な実装タスクを効率的に処理することで、プロダクトの価値を最大化し、市場投入までの時間を劇的に短縮します。

## リポジトリ構造

このリポジトリは、モノレポ構成となっており、主に以下の2つのコンポーネントが含まれています。

-   **`github_broker/`**:
    本プロジェクトのコアエンジン。GitHubリポジトリを監視し、タスクを自律型AIエージェントに割り当てる責務を持つ、常時稼働のバックエンドサービスです。
-   **`issue_creator_kit/`**:
    `_in_box` ディレクトリに置かれたMarkdown形式の計画ファイルから、GitHub Issueを自動生成するためのコマンドラインツール（CLI）です。`github_broker`への主要な入力を作成する役割を担います。

## アーキテクチャとドキュメント

本システムのアーキテクチャ、設計思想、および仕様は、以下のドキュメントにまとめられています。

-   **要求仕様 (ADRなど):**
    -   [`/reqs`](./reqs): `github_broker`のアーキテクチャ決定記録 (ADR) など。
    -   [`/issue_creator_kit/reqs`](./issue_creator_kit/reqs): `issue_creator_kit`のADRなど。
-   **設計ドキュメント:**
    -   [`/docs/architecture`](./docs/architecture): システム全体のアーキテクチャ概要、C4モデル、各種設計書。
    -   [`/issue_creator_kit/docs`](./issue_creator_kit/docs): `issue_creator_kit`の詳細な使い方や仕様。

**主要なドキュメント:**
-   [**System Context Diagram**](./docs/architecture/system_context.md)
-   [**Code Overview**](./docs/architecture/code-overview.md)

## Getting Started

プロジェクトをローカル環境でセットアップし、実行するための詳細な手順については、以下の公式ガイドを参照してください。

-   [**Getting Started Guide**](./docs/guides/getting-started.md)

このガイドには、必要なツールのインストール、依存関係のセットアップ、およびシステムの基本的な実行方法が含まれています。

## Contributing

本プロジェクトへの貢献に興味を持っていただきありがとうございます！
バグ報告、機能提案、プルリクエストなど、あらゆる形の貢献を歓迎します。

詳細は [CONTRIBUTING.md](./CONTRIBUTING.md) をご覧ください。

## License

このプロジェクトは [MIT License](./LICENSE) の下で公開されています。
```

## 完了条件 (Acceptance Criteria)
- `README.md` が、上記の「具体的な修正内容」で上書きされていること。

## 成果物 (Deliverables)
- 更新された `README.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/update-root-readme`
