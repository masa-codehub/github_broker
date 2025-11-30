---
title: "【Task】`redis-schema.md`を実装に合わせて全面的に更新"
labels: ["task", "documentation", "refactoring", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】`redis-schema.md`を実装に合わせて全面的に更新

## 親Issue (Parent Issue)
- (Story: `github_broker`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (なし)

## As-is (現状)
- `docs/architecture/redis-schema.md`に記述されているRedisのキースキーマが、`task_service.py`の実際の実装と大きく乖離している。
- Issueオブジェクトのキャッシュ (`issue:*`) や、エージェントの現在タスク (`agent_current_task:*`) など、実装で使われている重要なキーがドキュメントに全く記載されていない。

## To-be (あるべき姿)
- `redis-schema.md`が、`task_service.py`で実際に使用されている全てのRedisキーのフォーマット、データ型、目的、ライフサイクルを正確に反映した内容になる。
- 第三者がドキュメントを読むだけで、Redis上でどのようなデータがどのように管理されているかを完全に理解できる状態になる。

## ユーザーの意図と背景の明確化
- ユーザーは、Redis上のデータ構造がブラックボックス化している現状を問題視している。正確なドキュメントを整備することで、デバッグや新機能開発の際に、Redisの状態を正しく理解し、安全に変更できる状態にすることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `docs/architecture/redis-schema.md`
- **修正方法:** ファイル全体を以下の内容で**上書き**する。

```markdown
# Redisキースキーマ 設計書

## 1. 概要

このドキュメントは、`github_broker`プロジェクトにおけるRedisの利用方法、特にキーの命名規則と構造（スキーマ）について説明します。

本プロジェクトでは、Redisを主に以下の目的で利用しています。
- **Issueのキャッシュ:** GitHub APIへのアクセスを減らすためのIssueデータのキャッシュ。
- **分散ロック:** 複数のエージェントインスタンスが同一Issueを同時に処理することを防ぐためのロック。
- **状態管理:** エージェントの処理状況や、レビュータスクの遅延管理など。

## 2. キースキーマ一覧

| キーフォーマット                               | 型      | 説明                                                                                                                              | 主な利用者                         | TTLの目安      |
| ---------------------------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | -------------- |
| `issue:{issue_id}`                             | `String`  | GitHub IssueオブジェクトのJSONシリアライズ文字列。プライマリキャッシュとして機能する。                                              | `redis_client.sync_issues`         | なし（手動削除） |
| `issue_lock:{issue_id}`                        | `String`  | 特定Issueが処理中であることを示す分散ロック。値にはロックを取得した`agent_id`が設定される。                                     | `task_service` (acquire/release)   | 600秒          |
| `review_issue_detected_timestamp:{issue_id}`   | `String`  | `needs-review`ラベルを持つIssueを初めて検出したUTC時刻（ISO 8601形式）。レビュータスクの遅延割り当てに使用。                 | `task_service._find_review_task`   | なし（手動削除） |
| `agent_current_task:{agent_id}`                | `String`  | 特定のエージェントが現在割り当てられている`issue_id`を保持する。                                                              | `task_service`                     | 3600秒         |
| `task_candidate:{issue_id}:{agent_id}`         | `String`  | （現在未使用の可能性あり）タスク候補の情報を保持する。                                                                          | `task_service.create_task_candidate` | 86400秒        |
| `task:fix:{pull_request_number}`               | `String`  | レビューコメントから生成された修正タスクの情報をJSON形式で保持する。                                                            | `task_service.create_fix_task`     | 86400秒        |

## 3. 主要な利用フロー

### 3.1. Issueのキャッシュ (`issue:*`)

1.  `task_service.start_polling` が定期的に `github_client.get_open_issues` を呼び出します。
2.  取得したIssueリストは `redis_client.sync_issues` に渡されます。
3.  `sync_issues` は、各Issueを `issue:{issue_id}` というキーでRedisに保存します。この際、既存の `issue:*` キーは一度すべて削除され、常に最新の状態が保たれます。

### 3.2. 分散ロック (`issue_lock:*`)

1.  `task_service._find_first_assignable_task` 内で、割り当て候補のIssueが見つかると、`redis_client.acquire_lock("issue_lock:{issue_id}", agent_id)` を呼び出します。
2.  このメソッドは内部でRedisの `SETNX` (SET if Not eXists) コマンドを実行し、アトミックにロックを取得します。
3.  ロック取得に成功した場合のみ、後続のタスク割り当て処理が実行されます。
4.  処理中にエラーが発生した場合は、明示的に `release_lock` が呼ばれます。そうでなければ、キーはTTL（600秒）で自動的に失効し、デッドロックを防ぎます。
```

## 完了条件 (Acceptance Criteria)
- `docs/architecture/redis-schema.md` が、上記の「具体的な修正内容」で上書きされていること。

## 成果物 (Deliverables)
- 更新された `docs/architecture/redis-schema.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/update-redis-schema-doc`
