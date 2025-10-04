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

## 4. コード修正プロンプトの仕様

`GeminiExecutor`は、レビューコメント修正タスクのために、以下の構造を持つプロンプトを生成します。このプロンプトは、特定のPull Request (PR) とそのレビューコメントのコンテキストをAIエージェントに提供し、適切なコード修正を促すことを目的としています。

### 4.1. プロンプトテンプレート構造

プロンプトテンプレートはYAMLファイル（例: `github_broker/infrastructure/prompts/gemini_executor.yml`）内で定義され、以下のプレースホルダーを使用して動的に情報が埋め込まれます。

```yaml
# gemini_executor.yml (例)
review_comment_correction_prompt: |
  あなたは熟練したソフトウェアエンジニアです。
  以下のPull Requestのレビューコメントに基づいて、コード修正を行ってください。

  Pull Request URL: {{ pr_url }}
  レビューコメント:
  ```
  {{ review_comment_body }}
  ```

  修正が必要なファイルは以下の通りです。
  {{ file_diffs }}

  あなたの修正は、レビューコメントの意図を正確に反映し、既存のコードベースの品質基準を満たす必要があります。
  修正が完了したら、変更をコミットし、Pull Requestを更新してください。
```

### 4.2. プレースホルダーと埋め込み情報

`GeminiExecutor`は、`build_prompt`メソッドが呼び出された際に、以下の情報を対応するプレースホルダーに埋め込みます。

| プレースホルダー        | 説明                                                              | 取得元                                                              |
| :-------------------- | :---------------------------------------------------------------- | :------------------------------------------------------------------ |
| `{{ pr_url }}`        | 修正対象のPull RequestのURL。                                     | GitHub APIから取得したPull Request情報                              |
| `{{ review_comment_body }}` | 修正の根拠となるレビューコメントの本文。                          | GitHub APIから取得したレビューコメント情報                          |
| `{{ file_diffs }}`    | 修正対象ファイルの差分情報。                                      | GitHub APIから取得したPull Requestのファイル差分情報                |

この構造により、AIエージェントは具体的なPRのコンテキストとレビューコメントの内容を直接プロンプトとして受け取り、効率的かつ正確なコード修正作業を行うことができます。