# 概要
デザインドキュメント: Geminiモデルの更新とレビューIssueの処理

- **Author(s)**: SYSTEM_ARCHITECT
- **Status**: 提案中
- **Last Updated**: 2025-10-18

このドキュメントは、エージェントが使用するGeminiモデルのバージョン更新と、レビューが必要なIssueの検索条件および処理フローの変更を提案するものです。これにより、エージェントの実行コストの最適化と、レビュープロセスの効率化を目指します。

現在、開発タスク（`development`）を実行するエージェントは `gemini-2.5-flash` モデルを使用していますが、より新しくコスト効率の良いモデルが利用可能です。また、レビュー対象のIssueを検出する現在のロジックは、より効率的な検索クエリに改善の余地があります。さらに、検出からユーザーへの通知までの間に意図的な遅延を設けることで、関連するCI/CDプロセスが完了するのを待つなど、より安定した運用が可能になります。

## ゴール

### 機能要件 (Functional Requirements)

- `agents_main.py` で `development` タスクタイプに指定されているGeminiモデルを `gemini-flash-latest` に変更する。
- レビュー対象Issueの検索クエリを `is:issue label:needs-review linked:pr is:open` に変更する。
- レビュー対象のIssueが検出されてから、クライアントにタスクとして渡されるまでに一定時間の遅延を設ける。

### 非機能要件 (Non-Functional Requirements)

- エージェント実行の運用コストを削減する。
- レビュータスクの割り当て精度を向上させる。

## 設計

### 4.1. High-Level Design (ハイレベル設計)

1.  **`agents_main.py` の修正:**
    - `task_type` が `development` の場合に `gemini_model` を `"gemini-flash-latest"` に設定するロジックを修正します。

2.  **`TaskService` の修正 (`github_broker/application/task_service.py`):**
    - レビューIssueを検索するメソッド（`_find_review_task` など）のGitHub検索クエリを `is:issue label:needs-review linked:pr is:open` に更新します。
    - 検索でIssueが見つかった場合、すぐにタスクとして返さず、Redisなどの永続ストアに `issue_id` と `found_timestamp` を記録します。
    - `request_task` が呼び出された際に、永続ストア内のIssueをチェックし、`found_timestamp` から一定時間（例: 5分）が経過しているもののみをタスクとしてクライアントに返却します。経過していない場合は、タスクがないものとして応答します。

- **遅延ロジックをクライアント側 (`agents_main.py`) に実装する案:**
    - **採用しなかった理由:** 複数のエージェントクライアントが同じタスクを重複して処理しようとする可能性があり、状態管理が複雑になります。タスクの割り当て管理はサーバーサイド（Broker）の責務であるため、サーバーサイドで一元管理するのが適切です。

- 変更による新たなセキュリティリスクは想定されません。

## 考慮事項

- 遅延させる具体的な時間（秒数）は、CI/CDの平均実行時間などを考慮して決定する必要があります。まずは5分を初期値として提案します。

- `development` タスクを実行するエージェントのログに、使用モデルとして `gemini-flash-latest` が記録されること。
- `is:issue label:needs-review linked:pr is:open` の条件に合致するIssueが作成された場合、即座にはタスクとして割り当てられず、設定された遅延時間経過後に `request_task` を呼び出したクライアントに割り当てられること。
- 上記条件に合致しないIssueは、タスクとして割り当てられないこと。


(未着手)
