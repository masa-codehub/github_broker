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