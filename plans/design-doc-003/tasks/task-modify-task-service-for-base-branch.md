# 【Task】`TaskService` に `base_branch_name` の処理を追加する

## 目的とゴール / Purpose and Goals
このTaskの目的は、`TaskService` がタスクの種類に応じて `base_branch_name` を特定し、Redisへの保存、および `GeminiExecutor` への引き渡しを行うように責務を修正することです。

## 実施内容 / Implementation
- `github_broker/application/task_service.py` を修正し、`base_branch_name` を処理するロジックを追加します。
- 関連するテストコードを、新しいロジックを網羅するように修正します。

## 検証結果 / Validation Results
- `TaskService` がタスクの種類に応じて `base_branch_name` を正しく特定・処理し、テストが成功すること。

## 影響範囲と今後の課題 / Impact and Future Issues
- 影響範囲: `TaskService` のタスク処理ロジック。
- 今後の課題: なし。

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `docs/design-docs/003-prompt-template-updates.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- `TaskService` は `base_branch_name` を扱っていない。

## To-be (あるべき姿)
- `TaskService` が、タスクの種類に応じて `base_branch_name` を特定する。
- 特定した `base_branch_name` をRedisに保存する。
- `GeminiExecutor` を呼び出す際に、取得した `base_branch_name` を引数として渡す。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/application/task_service.py` を開く。
2. タスク実行の中核となるメソッド（例: `run_task`）を修正する。
3. タスクのペイロードを基に、タスクの種類を判定する（例: IssueがPRに紐づくか否かで、レビュータスクか新規開発タスクかを判断する）。
4. **レビュータスクの場合:** Issueペイロード内のPR情報から `base.ref` を `base_branch_name` として取得する。
5. **新規開発タスクの場合:** GitHub APIを呼び出して、リポジトリのデフォルトブランチ名を取得し、それを `base_branch_name` とする。
6. 取得した `base_branch_name` をRedisのタスク情報に保存する。
7. `gemini_executor.build_prompt` を呼び出す際に、引数として `base_branch_name` を渡す。
8. 上記のロジック分岐（レビュータスク、新規開発タスク）を網羅する単体テストを `tests/application/test_task_service.py` に追加・修正する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。

## 成果物 (Deliverables)
- 更新された `github_broker/application/task_service.py`
- 更新された `tests/application/test_task_service.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/add-base-branch-name-variable`
- **作業ブランチ (Feature Branch):** `task/modify-task-service-for-base-branch`
