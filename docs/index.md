# ドキュメントポータル

このページは、`github-broker`プロジェクトの全ての技術ドキュメントへの入り口です。

## 1. 設計思想とアーキテクチャ

システムの全体像、設計原則、コンポーネント間の連携方法について理解したい場合は、こちらを参照してください。

*   [システム設計書](./architecture/index.md)
*   [コード概要](./architecture/code-overview.md)
*   [CI/CD環境](./architecture/ci-cd-environment.md)
*   [DIコンテナ](./architecture/di-container.md)
*   [運用・デプロイ要件](./architecture/operational-requirements.md)
*   [Redisスキーマ](./architecture/redis-schema.md)


## 2. 開発者向けガイド

開発を始めるために必要な手順や、知っておくべきワークフローについて説明します。

- **[開発ワークフロー](./guides/development-workflow.md):** Issue起票からマージまでの流れを定義します。
- **[AgentClient利用ガイド](./guides/agent-client-guide.md):** 外部エージェントが本システムと連携するためのクライアントライブラリの使用方法を説明します。
- **[Gemini Executorガイド](./guides/gemini-executor-guide.md):** タスクの優先順位付けを行うGemini Executorの利用方法を説明します。

## 3. 仕様

特定の機能やエージェントの振る舞いに関する詳細な仕様です。

- **[エージェントペルソナ](./specs/agent-persona.md):** 各AIエージェントの役割と能力を定義します。