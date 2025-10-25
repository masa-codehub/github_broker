# 【Task】Redisスキーマから `review_comments` を削除する

## 目的とゴール / Purpose and Goals
このTaskの目的は、Redisのタスクハッシュから `review_comments` フィールドを削除し、関連するドキュメントとコードを更新することです。

## 実施内容 / Implementation
- `github_broker/domain/task.py` の `Task` データクラスから `review_comments` を削除します。
- `github_broker/infrastructure/redis_client.py` で `review_comments` を扱っている箇所を削除・修正します。
- `docs/architecture/redis-schema.md` を更新し、`review_comments` フィールドを削除します。
- 関連するテストコードを修正します。

## 検証結果 / Validation Results
- Redisスキーマから `review_comments` が削除され、テストが成功すること。

## 影響範囲と今後の課題 / Impact and Future Issues
- 影響範囲: `Task` ドメインモデル, `RedisClient`, Redisスキーマドキュメント。
- 今後の課題: なし。

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `docs/design-docs/003-prompt-template-updates.md`

## 実装の参照資料 (Implementation Reference Documents)
- `docs/architecture/redis-schema.md`

## As-is (現状)
- Redisのタスクハッシュに `review_comments` フィールドが存在する。

## To-be (あるべき姿)
- Redisのタスクハッシュから `review_comments` フィールドが削除されている。
- `docs/architecture/redis-schema.md` が更新されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/domain/task.py` の `Task` データクラスから `review_comments` を削除する。
2. `github_broker/infrastructure/redis_client.py` で `review_comments` を扱っている箇所を削除・修正する。
3. `docs/architecture/redis-schema.md` を更新し、`review_comments` フィールドを削除する。
4. 関連するテストコードを修正する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。

## 成果物 (Deliverables)
- 更新された `github_broker/domain/task.py`
- 更新された `github_broker/infrastructure/redis_client.py`
- 更新された `docs/architecture/redis-schema.md`
- 更新された `tests/domain/test_task.py`
- 更新された `tests/infrastructure/test_redis_client.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/remove-review-comments-variable`
- **作業ブランチ (Feature Branch):** `task/modify-redis-schema-for-review-comments`