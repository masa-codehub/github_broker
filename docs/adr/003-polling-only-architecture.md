# 概要 / Summary
[ADR-003] ポーリング方式アーキテクチャへの完全移行

- Status: Accepted
- Date: 2025-10-19

## 状況 / Context

ユーザーからの戦略的指示に基づき、プロジェクトのアーキテクチャをWebhookベースから、GitHub APIを定期的に確認する「ポーリング方式」に完全に切り替えることが決定されました。この決定は、ローカルでの開発体験を簡素化し、外部に公開するエンドポイントを持つことの複雑さを排除することを目的としています。これにより、セットアップが容易になり、セキュリティリスクも低減されます。

## 決定 / Decision

今後、本プロジェクトにおけるタスク取得のメカニズムは、GitHub APIへのポーリング方式を唯一の公式な方法とします。Webhookに関連するすべての技術（APIエンドポイント、サービス、設定など）は廃止され、新規開発やリファクタリングにおいて使用を禁止します。

## 結果 / Consequences

### メリット (Positive consequences)
- **`WebhookService` の廃止:** `github_broker/application/webhook_service.py` および関連するインターフェース（`api.py`内のエンドポイントなど）は、今後のリファクタリング作業で完全に削除されます。
- **`TaskService` の責務変更:** `TaskService` は、GitHub APIを定期的にポーリングしてIssue情報をローカルキャッシュ（Redis）に同期する責務を担うように変更されます。このポーリング処理は、独立したバックグラウンドプロセスとして起動されることを想定しています。
- **`docs/design-docs/webhook-based-architecture.md` の廃止:** このアーキテクチャドキュメントは現状と一致しなくなるため、**廃止 (Deprecated)** されます。今後のアーキテクチャに関する参照は、このADRおよび将来作成されるポーリング方式の設計ドキュメントを参照してください。

### デメリット (Negative consequences)
- **リアルタイム性の低下:** ポーリング方式であるため、Issueの変更がシステムに反映されるまでに遅延が生じます。

## 検証基準 / Verification Criteria
- Webhook関連のコードが削除されていること。
- `TaskService` がポーリング処理を実装していること。

## 実装状況 / Implementation Status

完了
