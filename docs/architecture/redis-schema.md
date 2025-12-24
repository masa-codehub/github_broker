# Redisキースキーマ 設計書

## 1. 概要

このドキュメントは、`github_broker`プロジェクトにおけるRedisの利用方法、特にキーの命名規則と構造（スキーマ）について説明します。

本プロジェクトでは、Redisを主に以下の目的で利用しています。
- **Issueのキャッシュ:** GitHub APIへのアクセスを減らすためのIssueデータのキャッシュ。
- **分散ロック:** 複数のエージェントインスタンスが同一Issueを同時に処理することを防ぐためのロック。
- **状態管理:** エージェントの処理状況や、レビュータスクの遅延管理など。

## 2. キースキーマ一覧

| キーフォーマット                               | 型                   | 説明                                                                                                                              | 主な利用者                         | TTLの目安      |

| ---------------------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | -------------- |

| `issue:{issue_id}`                             | `String (JSON)`      | GitHub IssueオブジェクトのJSONシリアライズ文字列。プライマリキャッシュとして機能する。                                              | `redis_client.sync_issues`         | なし（手動削除） |

| `issue_lock_{issue_id}`                        | `String (agent_id)`  | 特定Issueが処理中であることを示す分散ロック。値にはロックを取得した`agent_id`が設定される。                                     | `task_service` (acquire/release)   | 600秒          |

| `review_issue_detected_timestamp:{issue_id}`   | `String (ISO 8601)`  | `needs-review`ラベルを持つIssueを初めて検出したUTC時刻（ISO 8601形式）。レビュータスクの遅延割り当てに使用。                 | `task_service._find_review_task`   | なし（手動削除） |

| `agent_current_task:{agent_id}`                | `String (issue_id)`  | 特定のエージェントが現在割り当てられている`issue_id`を保持する。                                                              | `task_service`                     | 3600秒         |

| `task_candidate:{issue_id}:{agent_id}`         | `String (JSON)`      | タスク候補の情報を保持する。                                                                          | `task_service.create_task_candidate` | 86400秒        |

| `task:fix:{pull_request_number}`               | `String (JSON)`      | レビューコメントから生成された修正タスクの情報をJSON形式で保持する。                                                            | `task_service.create_fix_task`     | 86400秒        |

## 3. 主要な利用フロー

### 3.1. Issueのキャッシュ (`issue:*`)

1.  `task_service.start_polling` が定期的に `github_client.get_open_issues` を呼び出します。
2.  取得したIssueリストは `redis_client.sync_issues` に渡されます。
3.  `sync_issues` は、各Issueを `issue:{issue_id}` というキーでRedisに保存します。この際、既存の `issue:*` キーは一度すべて削除され、常に最新の状態が保たれます。

### 3.2. 分散ロック (`issue_lock_*`)

1.  `task_service._find_first_assignable_task` 内で、割り当て候補のIssueが見つかると、`redis_client.acquire_lock("issue_lock_{issue_id}", agent_id)` を呼び出します。
2.  このメソッドは内部でRedisの `SETNX` (SET if Not eXists) コマンドを実行し、アトミックにロックを取得します。
3.  ロック取得に成功した場合のみ、後続のタスク割り当て処理が実行されます。
4.  処理中にエラーが発生した場合は、明示的に `release_lock` が呼ばれます。そうでなければ、キーはTTL（600秒）で自動的に失効し、デッドロックを防ぎます。
