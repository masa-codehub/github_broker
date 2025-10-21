# 目的とゴール
# Issue: #1521
Status: Open
# 【Epic】Geminiモデルの更新とレビューIssue処理の改善

## 親Issue (Parent Issue)
- (なし)

## 子Issue (Sub-Issues)
- #1522
- #1523

## As-is (現状)
- `development`タスクを実行するエージェントは `gemini-2.5-flash` モデルを使用している。
- レビュー対象のIssueを検出するロジックが最適化されておらず、検出後すぐにタスクとして割り当てられる。

## To-be (あるべき姿)
- `development`タスクを実行するエージェントは、よりコスト効率の良い `gemini-flash-latest` モデルを使用する。
- レビュー対象Issueの検索が効率化され、検出から一定時間経過後にタスクとして割り当てられるようになることで、CI/CDプロセスとの連携が安定する。

## 完了条件 (Acceptance Criteria)
- [ ] Story: `development`タスクのGeminiモデルを`gemini-flash-latest`に更新する
- [ ] Story: レビュー対象Issueの検索ロジックと遅延処理を実装する

## 実施内容

## 検証結果

## 成果物 (Deliverables)
- `github_broker/application/task_service.py`
- `agents_main.py`
- `docs/architecture/redis-schema.md`
- `docs/architecture/request-task-sequence.md`

## 影響範囲と今後の課題

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-design-doc-001`
