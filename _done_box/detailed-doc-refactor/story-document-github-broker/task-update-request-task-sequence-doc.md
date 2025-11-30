---
title: "【Task】`request-task-sequence.md`をADR-015, ADR-016を反映した実装に同期"
labels: ["task", "documentation", "refactoring", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】`request-task-sequence.md`をADR-015, ADR-016を反映した実装に同期

## 親Issue (Parent Issue)
- (Story: `github_broker`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `reqs/adr/015-strict-priority-bucket-assignment.md`
- `reqs/adr/016-fix-review-issue-assignment-logic.md`

## As-is (現状)
- `docs/architecture/request-task-sequence.md` が、タスク割り当ての単純なフローしか記述していない。
- `task_service.py`に実装されている以下の重要なビジネスルールがドキュメントに反映されていない。
  1. **厳格な優先度フィルタリング(ADR-015):** 全Issueから最高優先度を特定し、その優先度のタスクのみを候補とするロジック。
  2. **タスク種別の分岐(ADR-016):** `needs-review`ラベルの有無による、開発タスクとレビュー修正タスクの処理分岐。
  3. **レビュータスクの遅延割り当て:** Redisのタイムスタンプを利用した、一定時間経過後の割り当てロジック。

## To-be (あるべき姿)
- `request-task-sequence.md`のシーケンス図と説明が、上記1, 2, 3のロジックを全て反映した、現状の実装と完全に一致した内容になる。
- 開発者がドキュメントを読むだけで、複雑なタスク選択・割り当てのフローを正確に理解できる状態になる。

## ユーザーの意図と背景の明確化
- ユーザーは、プロジェクトで最も複雑なビジネスロジックの一つであるタスク割り当てフローが、ブラックボックス化していることを問題視している。正確なシーケンス図を整備することで、ロジックの理解を助け、将来の仕様変更やデバッグを容易にすることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `docs/architecture/request-task-sequence.md`
- **修正方法:** ファイル全体を以下の内容で**上書き**する。

```markdown
# タスク要求シーケンス図

## 概要

このドキュメントは、エージェントが `/request-task` エンドポイントを呼び出してから、最適なタスクが割り当てられるまでの、サーバーサイド (`TaskService`) の一連の処理フローをシーケンス図として示します。

このフローは、以下のADRで定義された重要なビジネスルールに基づいています。
- **ADR-015:** 厳格な優先度に基づくタスク選択
- **ADR-016:** レビュー修正タスクのプロンプト生成

## シーケンス図

```mermaid
sequenceDiagram
    participant Agent
    participant API as /request-task
    participant TaskService
    participant Redis
    participant GitHub

    Agent->>+API: タスクをリクエスト (agent_id)
    API->>+TaskService: request_task(agent_id)

    %% フェーズ1: 全Issueから最高優先度を特定 (ADR-015)
    TaskService->>+Redis: 全Issueキャッシュを取得 (issue:*)
    Redis-->>-TaskService: Issueリスト(JSON)
    TaskService->>TaskService: 全ラベルから最高優先度を決定 (例: 'P0')

    %% フェーズ2: 候補タスクのフィルタリング
    TaskService->>TaskService: 候補Issueをフィルタリング
    Note right of TaskService: 1. 最高優先度ラベルを持つ<br/>2. 担当役割ラベルを持つ<br/>3. 'in-progress'でない<br/>4. story/epicでない

    %% フェーズ3: 候補タスクのループ処理
    loop 各候補タスク
        TaskService->>TaskService: 割り当て可能かチェック

        alt 開発タスク (needs-reviewラベルなし)
            Note right of TaskService: 通常の開発タスクとして処理
        else レビュー修正タスク (needs-reviewラベルあり)
            TaskService->>+Redis: 検出タイムスタンプを取得
            Redis-->>-TaskService: タイムスタンプ
            alt 遅延時間未経過
                TaskService->>TaskService: スキップ
                continue
            else 遅延時間経過
                Note right of TaskService: レビュータスクとして処理
            end
        end

        %% フェーズ4: ロック取得とタスク割り当て
        TaskService->>+Redis: 分散ロックを取得 (acquire_lock issue_lock:{issue_id})
        alt ロック取得失敗
            Redis-->>-TaskService: 失敗
            TaskService->>TaskService: 次の候補へ
            continue
        else ロック取得成功
            Redis-->>-TaskService: 成功
            TaskService->>+GitHub: ラベル追加 ('in-progress', agent_id)
            GitHub-->>-TaskService: 成功
            TaskService->>+GitHub: ブランチ作成
            GitHub-->>-TaskService: 成功

            alt レビュー修正タスクの場合 (ADR-016)
                TaskService->>+GitHub: PRとレビューコメントを取得
                GitHub-->>-TaskService: PR情報
                TaskService->>TaskService: レビュー修正用プロンプトを生成
            else 開発タスクの場合
                TaskService->>TaskService: 開発用プロンプトを生成
            end

            TaskService->>+API: TaskResponseを返却
            API-->>-Agent: タスク情報を返す
            break ループ終了
        end
    end

    alt 割り当てタスクなし
        TaskService-->>-API: None
        API-->>-Agent: 204 No Content
    end

```

## 主要ステップの詳細解説

1.  **最高優先度の決定 (ADR-015):**
    `request_task`が呼び出されると、まずRedisにキャッシュされている全てのIssueのラベルを走査し、最も優先度の高いレベル（例: 'P0'）を特定します。

2.  **候補タスクのフィルタリング:**
    特定された最高優先度ラベルを持つIssueのみが、割り当ての初期候補となります。ここからさらに、役割ラベルの有無や、処理中ではないかといった条件で絞り込まれます。

3.  **レビュータスクの遅延処理:**
    候補が`needs-review`タスクの場合、すぐに割り当てられません。Redisに保存された検出タイムスタンプを確認し、設定された遅延時間（例: 5分）が経過している場合のみ、割り当てプロセスに進みます。これにより、CI/CDプロセスとの競合を防ぎます。

4.  **分散ロックとアトミックな割り当て:**
    最終的な候補タスクに対して、Redisの`SETNX`コマンドを利用した分散ロックを取得します。ロックに成功した場合にのみ、タスクの割り当て（GitHubラベル付与、ブランチ作成）とプロンプト生成がアトミックに行われます。これにより、複数エージェントへの重複割り当てを完全に防ぎます。

5.  **タスク種別ごとのプロンプト生成 (ADR-016):**
    ロック取得後、`needs-review`ラベルの有無によってタスク種別を判断します。レビュー修正タスクの場合は、関連するPR情報やレビューコメントを取得し、それらを基に修正指示に特化したプロンプトを生成します。

```

## 完了条件 (Acceptance Criteria)
- `docs/architecture/request-task-sequence.md` が、上記の「具体的な修正内容」で上書きされていること。

## 成果物 (Deliverables)
- 更新された `docs/architecture/request-task-sequence.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/update-request-task-sequence-doc`
