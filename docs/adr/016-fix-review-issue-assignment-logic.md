# 概要 / Summary
[ADR-016] レビュー修正タスクのワークフロー改善

- **Status**: 提案中
- **Date**: 2025-10-25

## 状況 / Context

`task_service.py` の `start_polling` メソッドは、定期的にGitHubからIssueを取得し、Redisにキャッシュしています。しかし、現在の実装では「レビュー修正タスク」をエージェントに適切に割り当て、実行させるための一連のワークフローが未完成であり、以下の3つの問題点が存在します。

**問題点1: レビュー修正タスクのキャッシュ漏れ（入口の問題）**
`_find_review_task` メソッド内で `get_review_issues`（レビュー修正タスク用）で取得したIssueのリストは、タイムスタンプが記録されるだけで、`sync_issues` が呼び出されず、**Issue本体のデータがRedisキャッシュに保存されていません。**
この実装漏れにより、タスク割り当て処理が参照するRedisキャッシュにレビュー修正タスクのデータが存在しないため、エージェントがタスクを要求しても、レビュー修正タスクが候補リストに上がってきません。結果として、エージェントはレビュー修正作業に着手できず、レビュー修正タスクがシステム内で滞留し、開発サイクルが遅延する原因となっています。

**問題点2: プロンプト生成に必要な情報取得ロジックの欠如（中間の問題）**
`review_fix_prompt_template` を使用してレビュー修正タスク用のプロンプトを生成するには、`pr_url`（プルリクエストのURL）と `review_comments`（レビューコメントのリスト）の情報が必須です。
しかし、現在の `_find_first_assignable_task` メソッド内では、これらの情報をIssueオブジェクトから取得したり、GitHub APIから追加で取得したりするロジックが実装されていません。

**問題点3: プロンプト切り替えロジックの欠如（出口の問題）**
`_find_first_assignable_task` メソッドは、タスクの種類（開発タスクかレビュー修正タスクか）を判別することはできます。
しかし、その判別結果に基づいて、適切なプロンプトテンプレート（開発用 `prompt_template` vs レビュー修正用 `review_fix_prompt_template`）を切り替えて生成するロジックが実装されていません。常に開発用のプロンプトが生成されてしまいます。

## 決定 / Decision

上記3つの問題を解決するため、以下の修正を行います。

**1. レビュー修正タスクのキャッシュ処理追加（問題点1の解決）**
`github_broker/application/task_service.py` の `_find_review_task` メソッドを修正します。
具体的には、`self.github_client.get_review_issues()` を呼び出してレビューIssueのリスト（`review_issues`）を取得した直後に、`self.redis_client.sync_issues(review_issues)` の呼び出しを1行追加します。

**変更前:**
```python
# github_broker/application/task_service.py

    def _find_review_task(self) -> None:
        logger.info("Searching for review issues...")
        try:
            review_issues = self.github_client.get_review_issues()
            for issue in review_issues:
                issue_id = issue.get("number")
                if issue_id:
                    timestamp_key = self.REVIEW_ISSUE_TIMESTAMP_KEY_FORMAT.format(
                        issue_id=issue_id
                    )
                    if not self.redis_client.get_value(timestamp_key):
                        self.redis_client.set_value(
                            timestamp_key, datetime.now(UTC).isoformat()
                        )
                        logger.info(
                            f"[issue_id={issue_id}] Detected review issue and stored timestamp in Redis."
                        )
        except GithubException as e:
            logger.error(
                f"An error occurred while searching for review issues: {e}",
                exc_info=True,
            )
```

**変更後:**
```python
# github_broker/application/task_service.py

    def _find_review_task(self) -> None:
        logger.info("Searching for review issues...")
        try:
            review_issues = self.github_client.get_review_issues()
            # 取得したレビューIssueのリストをRedisキャッシュに同期
            self.redis_client.sync_issues(review_issues) # <- この行を追加
            for issue in review_issues:
                issue_id = issue.get("number")
                if issue_id:
                    timestamp_key = self.REVIEW_ISSUE_TIMESTAMP_KEY_FORMAT.format(
                        issue_id=issue_id
                    )
                    if not self.redis_client.get_value(timestamp_key):
                        self.redis_client.set_value(
                            timestamp_key, datetime.now(UTC).isoformat()
                        )
                        logger.info(
                            f"[issue_id={issue_id}] Detected review issue and stored timestamp in Redis."
                        )
        except GithubException as e:
            logger.error(
                f"An error occurred while searching for review issues: {e}",
                exc_info=True,
            )
```

**2. プロンプト生成に必要な情報取得ロジックの追加（問題点2の解決）**
`github_broker/application/task_service.py` の `_find_first_assignable_task` メソッドを修正します。
レビュー修正タスク（`TaskType.REVIEW`）の場合に、以下の情報を取得するロジックを追加します。
- `pr_url`: `github_client.get_pr_for_issue(task.issue_id)` を呼び出して、Issueに紐づくプルリクエストのURLを取得します。
- `review_comments`: `github_client.get_pull_request_review_comments(pr_number)` を呼び出して、プルリクエストに付与されたレビューコメントのリストを取得します。
これらの情報は、`gemini_executor.build_code_review_prompt` メソッドの引数として使用されます。

**3. プロンプト切り替えロジックの追加（問題点3の解決）**
`github_broker/application/task_service.py` の `_find_first_assignable_task` メソッド内のプロンプト生成ロジックを修正します。
タスクの種類を判別し、以下のように使用するプロンプトテンプレートを切り替えます。
- **開発タスク (`TaskType.DEVELOPMENT`) の場合:**
  - `gemini_executor.yml` の `prompt_template` を使用する `gemini_executor.build_prompt` メソッドを呼び出します。
- **レビュー修正タスク (`TaskType.REVIEW`) の場合:**
  - `gemini_executor.yml` の `review_fix_prompt_template` を使用する `gemini_executor.build_code_review_prompt` メソッドを呼び出します。
  - この際、問題点2で取得した `pr_url` と `review_comments` を引数として渡します。

## 結果 / Consequences

### メリット (Positive consequences)

- レビュー修正タスクがRedisキャッシュに正しく保存され、タスク割り当ての候補として認識されるようになります。
- レビュー修正タスクに必要な情報（PRのURL、レビューコメント）が取得できるようになります。
- タスクの種類に応じて適切なプロンプトが生成され、エージェントに渡されるようになります。
- これにより、「レビュー修正タスク」のワークフロー全体が機能するようになり、エージェントがレビューコメントに基づいた修正作業を効率的に行えるようになります。

### デメリット (Negative consequences)

- 特になし。これはシステムの機能改善とバグ修正を兼ねるものです。

## Verification Criteria (検証基準)

- `redis-cli` 等のツールでRedisの `issue:*` キーを確認し、`needs-review` ラベルを持つIssueのデータがキャッシュにJSON形式で保存されていること。
- 修正後、エージェントがタスクをリクエストした際に、`needs-review` ラベルを持つIssueがタスクとして割り当てられること。
- Brokerのログで、レビュー修正タスクが割り当てられる際、`gemini_executor.build_code_review_prompt` が使用され、開発タスクの際には `gemini_executor.build_prompt` が使用されていることが確認できること（要ログ追加）。
- エージェントに渡されるプロンプトの内容が、タスクの種類に応じて適切に異なっていること。

## Implementation Status (実装状況)
未着手
