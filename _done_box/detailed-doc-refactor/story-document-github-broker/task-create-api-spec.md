---
title: "【Task】`github_broker`のAPI仕様を新規作成"
labels:
  - "task"
  - "documentation"
  - "refactoring"
  - "P2"
  - "TECHNICAL_DESIGNER"
---
# 【Task】`github_broker`のAPI仕様を新規作成

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- story/document-github-broker

## As-is (現状)
- `github_broker/interface/api.py`でWeb APIが実装されているが、その仕様を定義したドキュメントが存在しない。

## To-be (あるべき姿)
- `docs/specs/github_broker_api.md`が新規作成されている。
- 上記ファイルには、`api.py`で定義されている全エンドポイントについて、HTTPメソッド、パス、リクエストのヘッダ・ボディ、レスポンスのステータスコード・ボディが、OpenAPI Specification(OAS)に準拠する形で記述されている。

## ユーザーの意図と背景の明確化
- ユーザーは、APIの実装そのものではなく、明確に定義された仕様書を開発の拠り所としたい。APIの利用者が実装を読まずとも、仕様書だけでAPIを正しく利用できる状態を目指している。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/interface/api.py`のソースコードを精査し、全エンドポイントの仕様を洗い出す。
2. `docs/specs/github_broker_api.md`を新規作成する。
3. 洗い出した仕様をOAS v3に準拠したYAMLまたはMarkdown形式で記述する。
4. 変更をコミットする。

## 完了条件 (Acceptance Criteria)
- `api.py`の全エンドポイントが`github_broker_api.md`に網羅されていること。
- 記述された仕様が、実際のエンドポイントの挙動と一致していること。

## 成果物 (Deliverables)
- 新規作成された `docs/specs/github_broker_api.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/create-api-spec`
