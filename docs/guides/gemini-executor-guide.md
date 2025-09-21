# `GeminiExecutor` 利用ガイド

## 1. 概要

このドキュメントは、`github-broker`ライブラリに含まれる`GeminiExecutor`クラスの利用方法を説明するガイドです。

`GeminiExecutor`は、サーバーサイドで動作するコンポーネントであり、特定のタスク（Issueの解決など）を実行するためにGoogleのGemini CLIツールを呼び出します。このExecutorは、与えられたタスク情報に基づいてGemini CLIに渡すプロンプトを生成し、その実行を管理します。これにより、エージェントがGitHubのIssueを解決するプロセスを自動化・効率化します。

## 2. 設定

`GeminiExecutor`を利用するには、以下の環境変数の設定が必須です。

- **`GEMINI_API_KEY`**: `GeminiExecutor`がGemini APIと通信するために使用します。サーバー環境に設定してください。

また、`GeminiExecutor`はプロンプトテンプレートをYAMLファイルから読み込みます。デフォルトのパスは`github_broker/infrastructure/prompts/gemini_executor.yml`です。このファイルを変更することで、プロンプトの挙動をカスタマイズできます。

## 3. `GeminiExecutor` の利用方法

### 3.1. 初期化

`GeminiExecutor`は、`log_dir`、`model`、`prompt_file`の各引数で初期化できます。`GEMINI_API_KEY`は環境変数から自動的に読み込まれます。

```python
import os
from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor

# 環境変数 GEMINI_API_KEY が設定されている必要がある
# ログディレクトリは任意で指定
log_directory = "/app/logs/gemini_executor"
executor = GeminiExecutor(
    log_dir=log_directory,
    model="gemini-1.5-flash", # 使用するGeminiモデル
    prompt_file="github_broker/infrastructure/prompts/gemini_executor.yml" # プロンプトテンプレートのパス
)
```

### 3.2. タスクの実行

`execute`メソッドに、タスクの詳細を含む辞書を渡すことで、Gemini CLIツールが実行されます。この辞書には、プロンプト生成に必要な`issue_id`, `title`, `body`, `branch_name`などの情報が含まれている必要があります。

#### コード例

```python
from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor

# Executorの初期化（上記参照）
log_directory = "/app/logs/gemini_executor"
executor = GeminiExecutor(
    log_dir=log_directory,
    model="gemini-1.5-flash",
    prompt_file="github_broker/infrastructure/prompts/gemini_executor.yml"
)

# 実行するタスクの例
# このタスクは、TaskServiceなどによって生成され、Executorに渡されることを想定しています。
task_to_execute = {
    "agent_id": "CODER_AGENT_1",
    "issue_id": 123,
    "title": "README.md のタイポを修正",
    "body": "README.md ファイルに 'typpo' というタイポがあります。これを 'typo' に修正してください。",
    "branch_name": "fix/readme-typo-123"
}

# タスクを実行
executor.execute(task=task_to_execute)

print(f"タスク (Issue ID: {task_to_execute['issue_id']}) の実行が開始されました。詳細はログディレクトリ ({log_directory}) を確認してください。")
```
