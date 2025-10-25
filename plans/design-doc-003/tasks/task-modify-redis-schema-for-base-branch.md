# 【Task】Redisスキーマに `base_branch_name` を追加する

## 目的とゴール / Purpose and Goals
このTaskの目的は、Redisのタスクハッシュに `base_branch_name` フィールドを追加し、関連するドキュメントとコードを更新することです。

## 実施内容 / Implementation
- `github_broker/domain/task.py` の `Task` データクラスに `base_branch_name` を追加します。
- `github_broker/infrastructure/redis_client.py` で `base_branch_name` を扱えるように修正します。
- `docs/architecture/redis-schema.md` を更新し、`base_branch_name` フィールドを追加します。
- 関連するテストコードを修正します。

## 検証結果 / Validation Results
- Redisスキーマに `base_branch_name` が追加され、テストが成功すること。

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
- Redisのタスクハッシュに `base_branch_name` フィールドが存在しない。

## To-be (あるべき姿)
- Redisのタスクハッシュに `base_branch_name` フィールドが追加されている。
- `docs/architecture/redis-schema.md` が更新されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/domain/task.py` の `Task` データクラスに `base_branch_name` を追加する。
2. `github_broker/infrastructure/redis_client.py` で `base_branch_name` を扱えるように修正する。
3. `docs/architecture/redis-schema.md` を更新し、`base_branch_name` フィールドを追加する。
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
- **ベースブランチ (Base Branch):** `story/add-base-branch-name-variable`
- **作業ブランチ (Feature Branch):** `task/modify-redis-schema-for-base-branch`