# 【Epic】ADR-015: 厳格な優先度バケットによるタスク割り当てを実装する

## 親Issue (Parent Issue)
- (なし)

## 子Issue (Sub-Issues)
- (起票後に追記)

## Issue: #1737
## Status: Open

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/015-strict-priority-bucket-assignment.md`

## 実装の参照資料 (Implementation Reference Documents)
- `github_broker/application/task_service.py`

# 目的とゴール / Purpose and Goals
タスク割り当てロジックを「厳格な優先度バケット方式」に変更し、ワークフローの予測可能性と依存関係の解決を優先する。

## As-is (現状)
現在のタスク割り当てロジックは、優先度の高いものから順にエージェントに割り当てる「ベストエフォート方式」であり、Issue間の前後関係（依存関係）を厳密に管理できない。

## To-be (あるべき姿)
ある優先度レベルのIssueがすべてクローズされるまで、次の優先度レベルのIssueには一切着手しない「厳格な優先度バケット方式」が導入され、ワークフローの予測可能性と依存関係の解決が保証されている。

## 目標達成までの手順 (Steps to Achieve Goal)

本Epicにおけるタスクの優先度は、Epic > Story > Task の階層で定義されます。数値が小さいほど優先度が高く、EpicはP4、StoryはP1〜P3、TaskはP0〜P2となります。ガントチャートは、この階層と依存関係を視覚的に示しています。

```mermaid
gantt
    title ADR-015 実装計画ガントチャート
    dateFormat  YYYY-MM-DD
    axisFormat  %m/%d

    %% --- Epic: ADR-015 厳格な優先度バケットによるタスク割り当てを実装する (P4) ---
    section Epic: ADR-015 Strict Priority Bucket Assignment (P4)
    全体計画 :crit, 2025-10-27, 12d

    %% --- Story 1: 現在の最高優先度を特定するロジックを実装する (P1) ---
    section Story 1: Implement Logic to Determine Current Highest Priority (P1)
    GitHub APIで優先度ラベル取得      :active, task-1.1, 2025-10-27, 1d, priority 0
    最高優先度特定関数実装         :active, task-1.2, after task-1.1, 1d, priority 0

    %% --- Story 2: タスク候補のフィルタリングロジックを実装する (P2) ---
    section Story 2: Implement Task Candidate Filtering Logic (P2)
    最高優先度レベルでフィルタリングロジック実装: task-2.1, after task-1.2, 2d, priority 1

    %% --- Story 3: タスク割り当てロジックを更新する (P3) ---
    section Story 3: Update Task Assignment Logic (P3)
    TaskServiceの割り当てロジック修正: task-3.1, after task-2.1, 2d, priority 2

    %% --- Story 4: 厳格な優先度バケット方式のテストを実装する (P3) ---
    section Story 4: Implement Strict Priority Bucket Testing (P3)
    P0とP1のIssueでP1が割り当てられないテスト追加: task-4.1, after task-3.1, 1d, priority 2
    P0完了後にP1が割り当てられるテスト追加      : task-4.2, after task-4.1, 1d, priority 2

    %% --- Story 5: ADR-015の変更点をドキュメント化する (P3) ---
    section Story 5: Document ADR-015 Changes (P3)
    開発者ガイド更新  : task-5.1, after task-4.2, 1d, priority 2
    設計ドキュメント更新      : task-5.2, after task-5.1, 1d, priority 2
```

1. `Story: 現在の最高優先度を特定するロジックを実装する` を行い、タスク割り当ての前提となる最高優先度を特定する。
2. `Story: タスク候補のフィルタリングロジックを実装する` を行い、最高優先度レベルのIssueのみを候補とする。
3. `Story: タスク割り当てロジックを更新する` を行い、フィルタリングされた候補リストに基づいてタスクを割り当てるように変更する。
4. `Story: 厳格な優先度バケット方式のテストを実装する` を行い、新しいロジックが正しく機能することを検証する。
5. `Story: ADR-015の変更点をドキュメント化する` を行い、新しいタスク割り当てルールに関するドキュメントを更新する。

## 完了条件 (Acceptance Criteria)
- このEpicを構成する全てのStoryの実装が完了していること。
- 各Storyの成果物を組み合わせた統合テストが成功し、関連する意思決定ドキュメント（ADR-015）の要求事項をすべて満たしていることが確認されること。

## 成果物 (Deliverables)
- `github_broker/application/task_service.py` (更新)
- `tests/application/test_task_service.py` (更新)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-adr-015`

## Status
Not Created