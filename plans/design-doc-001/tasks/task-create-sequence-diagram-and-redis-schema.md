# 【Task】シーケンス図とRedisスキーマを定義する

## 親Issue (Parent Issue)
- (起票後に追記)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/design-docs/001-update-gemini-model-and-review-issue-handling.md`

## 実装の参照資料 (Implementation Reference Documents)
- `docs/design-docs/001-update-gemini-model-and-review-issue-handling.md`
- `github_broker/application/task_service.py`
- `github_broker/infrastructure/redis_client.py`
- `github_broker/infrastructure/github_client.py`

## As-is (現状)
レビューIssueの遅延処理に関する、詳細なシーケンス図とRedisのデータ構造定義が存在しない。

## To-be (あるべき姿)
`TaskService`におけるレビューIssueの発見から、Redisへの保存、遅延後のタスク払い出しまでの一連の流れを示すシーケンス図が `docs/architecture/request-task-sequence.md` に追記されている。
また、遅延処理のためにRedis上で使用するキーの命名規則とデータ構造が `docs/architecture/redis-schema.md` に定義されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `TaskService`のロジックを分析し、遅延処理のシーケンスを明確にする。
2. Mermaid.jsなどを用いてシーケンス図を作成し、`request-task-sequence.md`を更新する。
3. 遅延管理に必要な情報を整理し、Redisのキー構造とデータ型を設計して`redis-schema.md`を更新する。
4. 更新されたドキュメントが完了条件を満たしていることを確認し、このTaskを完了とする。

## 完了条件 (Acceptance Criteria)
- 設計駆動開発の考え方に基づき、設計が完了していること。
- シーケンス図には、`TaskService`、`RedisClient`、`GitHubClient`間のインタラクションが正確に記述されていること。
- Redisスキーマ定義には、キー名、データ型（例: Hash, Sorted Set）、フィールド、値の具体例が明記されていること。

## 成果物 (Deliverables)
- `docs/architecture/request-task-sequence.md` (更新)
- `docs/architecture/redis-schema.md` (更新)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/create-technical-spec-for-review-handling`
- **作業ブランチ (Feature Branch):** `task/create-sequence-diagram-and-redis-schema`
