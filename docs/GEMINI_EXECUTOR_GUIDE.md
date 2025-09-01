# `GeminiExecutor` 利用ガイド

## 1. 概要

このドキュメントは、`github-broker`ライブラリに含まれる`GeminiExecutor`クラスの利用方法を説明するガイドです。

`GeminiExecutor`は、与えられたIssueリストに基づき、GoogleのGemini APIを利用して最適なIssueを選択するためのユーティリティです。これは、エージェントの役割（Role）に合致するタスクが複数存在する場合の、優先順位付けロジックとして利用できます。

## 2. インストール

本ライブラリは、GitHubリポジトリから直接pipを使用してインストールします。

```bash
pip install git+https://github.com/masa-codehub/github_broker.git
```

依存関係は`pyproject.toml`に定義されており、上記コマンドで自動的にインストールされます。

## 3. 設定

`GeminiExecutor`を利用するには、以下の環境変数の設定が必須です。

- **`GEMINI_API_KEY`**: `GeminiExecutor`がGemini APIと通信するために使用します。ご自身のAPIキーを設定してください。

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

## 4. `GeminiExecutor` の利用方法

### 4.1. 初期化

`GeminiExecutor`は、環境変数 `GEMINI_API_KEY` が設定されていれば、引数なしで初期化できます。

```python
from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor

# 環境変数 GEMINI_API_KEY が設定されている必要がある
executor = GeminiExecutor()
```

### 4.2. 最適なIssueの選択

`select_best_issue`メソッドに、Issueのリストを渡すことで、最適と判断されたIssueのID（`int`）が返されます。

- **`issues`**: `dict`のリスト。各`dict`は`id`, `title`, `body`, `labels`のキーを持つ必要があります。

Gemini APIとの通信に失敗した場合、このメソッドはフォールバックとしてリストの最初のIssueのIDを返します。

#### コード例

```python
from github_broker.infrastructure.executors.gemini_executor import GeminiExecutor

# Issue候補のリストを作成（役割によるフィルタリングは完了済みと仮定）
candidate_issues = [
    {
        "id": 101,
        "title": "UIのボタンの色を修正する",
        "body": "ログインボタンの色が赤すぎるので、青色に変更してください。",
        "labels": ["bug", "ui", "css", "CODER"]
    },
    {
        "id": 102,
        "title": "APIのパフォーマンスを改善する",
        "body": "ユーザープロファイルの取得APIが遅い。N+1問題を解決する必要がある。",
        "labels": ["performance", "backend", "python", "CODER"]
    }
]

# Executorの初期化
executor = GeminiExecutor()

# 最適なIssueを選択
selected_id = executor.select_best_issue(
    issues=candidate_issues
)

if selected_id is not None:
    print(f"選択されたIssue ID: {selected_id}")
    # 選択されたIssueを取得
    selected_issue = next((issue for issue in candidate_issues if issue['id'] == selected_id), None)
    print(f"選択されたIssueのタイトル: {selected_issue['title']}")
else:
    print("最適なIssueが見つかりませんでした。")

```