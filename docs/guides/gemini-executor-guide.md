# `GeminiExecutor` 利用ガイド

## 1. 概要

このドキュメントは、`github-broker`ライブラリに含まれる`GeminiExecutor`クラスの利用方法を説明するガイドです。

`GeminiExecutor`は、サーバーサイドで動作するコンポーネントであり、**AIエージェント（クライアント）に渡すためのプロンプトを生成する責務**を担います。具体的には、`TaskService`などのアプリケーションサービスから呼び出され、与えられたタスク情報とプロンプトテンプレートを基に、最終的なプロンプト文字列を組み立てます。

このコンポーネントはタスクを**実行**するのではなく、あくまで実行可能なプロンプトを**生成**することに特化しています。実際のタスク実行は、プロンプトを受け取ったクライアント側のエージェントが行います。

## 2. 設定

`GeminiExecutor`は、プロンプトテンプレートをYAMLファイルから読み込みます。このファイルのパスは、初期化時に指定する必要があります。

デフォルトのテンプレートパス:
`github_broker/infrastructure/prompts/gemini_executor.yml`

## 3. `GeminiExecutor` の利用方法（サーバーサイドでの統合）

`GeminiExecutor`は、主に`TaskService`のようなアプリケーション層のサービスから利用されることを想定しています。以下に、`TaskService`が`GeminiExecutor`をどのように利用してプロンプトを生成するかの例を示します。

### 3.1. 初期化と依存性注入

`GeminiExecutor`は、プロンプトテンプレートのパス（`prompt_file`）などを引数に初期化されます。通常、これはDIコンテナ（例: `punq`）を通じて`TaskService`に注入されます。

```python
# github_broker/infrastructure/di_container.py (抜粋)
import punq
import os
from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor
from github_broker.application.task_service import TaskService

container = punq.Container()

# GeminiExecutorをシングルトンとして登録
container.register(GeminiExecutor, instance=GeminiExecutor(
    prompt_file=os.getenv("GEMINI_EXECUTOR_PROMPT_FILE", "github_broker/infrastructure/prompts/gemini_executor.yml")
), scope=punq.Scope.singleton)

# TaskServiceは依存するExecutorをDIで受け取る
container.register(TaskService,
    factory=lambda: TaskService(
        # ... other dependencies
        gemini_executor=container.resolve(GeminiExecutor)
    ),
    scope=punq.Scope.singleton
)
```

### 3.2. `TaskService`からのプロンプト生成

`TaskService`は、割り当てるべきIssueの情報を取得した後、`GeminiExecutor`の`build_prompt`メソッドを呼び出して、クライアントに渡すためのプロンプト文字列を生成します。

```python
# github_broker/application/task_service.py (抜粋)
from github_broker.domain.task import Task
from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor

class TaskService:
    def __init__(
        self,
        # ... other dependencies
        gemini_executor: GeminiExecutor # DIでGeminiExecutorを受け取る
    ):
        # ...
        self.gemini_executor = gemini_executor

    def _find_first_assignable_task(self, candidate_issues: list, agent_id: str) -> TaskResponse | None:
        # ... (タスク選択ロジック)
        
        # 割り当てるタスクが決定したら、Executorを使ってプロンプトを生成する
        if assignable_task:
            try:
                # ... (ブランチ作成やラベル付与などの処理)

                prompt = self.gemini_executor.build_prompt(
                    issue_id=assignable_task.issue_id,
                    title=assignable_task.title,
                    body=assignable_task.body,
                    branch_name=branch_name
                )

                return TaskResponse(
                    # ... other fields
                    prompt=prompt
                )
            except Exception as e:
                # ... (エラーハンドリング)
        
        return None
```

この設計により、プロンプトの生成ロジックはサーバーサイドにカプセル化され、クライアントは受け取ったプロンプトを実行するだけのシンプルな責務に集中できます。

## 4. コード修正プロンプトの仕様（将来的な構想）

`GeminiExecutor`は、将来的にコード修正タスクのために以下の構造を持つプロンプトを生成する予定です。このプロンプトは、AIエージェントがGitHubのプルリクエスト（PR）と関連するレビューコメントを理解し、適切なコード修正を行うためのコンテキストを提供することを目的としています。

### 4.1. プロンプトテンプレートの構造

コード修正プロンプトは、主に以下のプレースホルダーを含むテンプレートに基づいています。

```yaml
# github_broker/infrastructure/prompts/gemini_executor.yml (将来的に追加予定の抜粋)
code_fix_prompt:
  template: |
    以下のGitHubプルリクエストのURLとレビューコメントを参考に、コード修正を行ってください。

    プルリクエストURL: {pr_url}

    レビューコメント:
    {review_comments}

    修正後のコードを提案してください。
```

- **`{pr_url}`**: 修正対象となるプルリクエストのURLが埋め込まれます。AIエージェントはこのURLを通じて、PRの変更内容、関連するIssue、およびその他のコンテキスト情報を取得できます。
- **`{review_comments}`**: プルリクエストに付与されたレビューコメントのテキストが埋め込まれます。これらのコメントは、AIエージェントが修正の意図や具体的な指示を理解するために不可欠です。

### 4.2. プルリクエストURLとレビューコメントの埋め込み

`GeminiExecutor`は、`build_code_fix_prompt`メソッド（実装予定）を通じて、以下の情報をプロンプトに埋め込むことを想定しています。

- **プルリクエストURL**: `github_client`から取得したプルリクエストのURLが直接`{pr_url}`に挿入されます。
- **レビューコメント**: `github_client`から取得したレビューコメントのリストを整形し、`{review_comments}`に挿入します。各コメントは、以下のフォーマットで整形されることを想定しています。
  - **整形ルール（プレースホルダー形式）**:
    `- @{author} ({file}:L{line}): {body}`
    - `@{author}`: コメントの投稿者
    - `{file}`: 対象ファイルのパス
    - `{line}`: 対象行番号
    - `{body}`: コメント本文

**例:**

```
プルリクエストURL: https://github.com/masa-codehub/github_broker/pull/123

レビューコメント:
- @reviewer1 (file.py:L10): この関数は引数のバリデーションが必要です。
- @reviewer2 (another_file.js:L25): 変数名が不明瞭です。より分かりやすい名前に変更してください。

修正後のコードを提案してください。
```

この詳細なプロンプト構造により、AIエージェントはコード修正タスクを効率的かつ正確に実行するための十分な情報を得ることができます。