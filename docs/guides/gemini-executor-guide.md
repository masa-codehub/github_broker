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

## 4. コード修正用プロンプトの仕様

`GeminiExecutor`は、AIエージェントがGitHubのプルリクエスト（PR）に対するレビューコメントに基づいてコード修正を行うためのプロンプトを生成します。このプロンプトは、エージェントが修正対象のPR、関連するレビューコメント、および修正に必要なコンテキストを正確に理解できるように設計されています。

### 4.1. プロンプトテンプレートの構造

コード修正用プロンプトは、以下の要素を組み合わせて構成されます。

-   **システム指示 (System Instruction):** エージェントの役割（コード修正担当）と、期待される行動（レビューコメントに基づく修正）を定義します。
-   **PR情報 (Pull Request Information):** 修正対象のPRに関する詳細情報（URL、タイトル、説明など）を提供します。これにより、エージェントはPRの全体像を把握できます。
-   **レビューコメント (Review Comments):** 修正の具体的な指示を含むレビューコメントの本文を提供します。複数のコメントがある場合は、それぞれが明確に区別されるように含めます。
-   **コードスニペット (Code Snippets):** レビューコメントが指摘しているコードの周辺部分を、コンテキストとして提供します。これにより、エージェントは修正箇所を特定しやすくなります。

### 4.2. PRのURLとレビューコメントの埋め込み

`GeminiExecutor`は、`build_code_correction_prompt`のような専用のメソッドを通じて、以下の情報をプロンプトに埋め込みます。

-   **PRのURL:** `https://github.com/{owner}/{repo}/pull/{pull_number}` の形式で、修正対象のPRへの直接リンクをプロンプト内に含めます。
-   **レビューコメント:** 各レビューコメントは、以下の形式でプロンプトに埋め込まれます。

    ```
    --- Review Comment ---
    File: {file_path}
    Line: {line_number}
    Comment: {comment_body}
    --- End Review Comment ---
    ```

    -   `{file_path}`: コメントが付けられたファイルのパス。
    -   `{line_number}`: コメントが付けられた行番号。
    -   `{comment_body}`: レビューコメントの本文。

### 4.3. プロンプト生成例

```
あなたはGitHubのプルリクエストに対するコード修正を担当するAIエージェントです。以下のレビューコメントに基づき、指定されたプルリクエストのコードを修正してください。

--- Pull Request Information ---
URL: https://github.com/masa-codehub/github_broker/pull/123
Title: Feature: Add new user authentication
Description: This PR introduces a new user authentication mechanism using OAuth2.

--- Review Comment ---
File: github_broker/application/user_service.py
Line: 45
Comment: Consider adding a try-except block for the external API call to handle potential network errors gracefully.
--- End Review Comment ---

--- Code Snippet (github_broker/application/user_service.py:40-50) ---
def authenticate_user(self, username, password):
    # ...
    response = external_auth_api.login(username, password) # <-- This line is pointed by the comment
    # ...
--- End Code Snippet ---

あなたの修正案を提案してください。
```
