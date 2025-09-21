# `AgentClient` 利用ガイド

## 1. 概要

このドキュメントは、`github-broker`システムと連携する外部AIエージェントを開発するためのガイドです。提供される`AgentClient`クラスを利用することで、タスク割り当てサーバーとの通信を容易に実装できます。

`AgentClient`は、タスク割り当てサーバーに新しいタスクを要求するためのHTTPクライアントです。

## 2. インストール

本ライブラリは、GitHubリポジトリから直接pipを使用してインストールします。

```bash
pip install git+https://github.com/masa-codehub/github_broker.git
```

依存関係は`pyproject.toml`に定義されており、上記コマンドで自動的にインストールされます。

## 3. `AgentClient` の利用方法

`AgentClient`は、エージェント自身の情報（IDや役割）とサーバーの接続情報を保持し、タスクの要求を行います。

### 3.1. 初期化

クライアントの初期化時に、エージェントの`agent_id`と`agent_role`、そして接続先のサーバー情報を渡します。

- `agent_id` (str): エージェントを一意に識別するID。
- `agent_role` (str): エージェントの役割を示す文字列 (例: `CODER`)。
- `host` (str): サーバーのホスト名。デフォルトは`localhost`。
- `port` (int): サーバーのポート番号。デフォルトは環境変数`APP_PORT`または`8080`。

```python
from github_broker import AgentClient

# エージェントの情報を定義
AGENT_ID = "my-python-agent-001"
AGENT_ROLE = "CODER"

# サーバーの接続情報を定義
SERVER_HOST = "localhost"
SERVER_PORT = 8000

# クライアントの初期化
client = AgentClient(
    agent_id=AGENT_ID,
    agent_role=AGENT_ROLE,
    host=SERVER_HOST,
    port=SERVER_PORT
)
```

### 3.2. タスクの要求

`request_task`メソッドを呼び出して、サーバーに新しいタスクを要求します。エージェントの情報は初期化時に渡しているため、このメソッドに引数は不要です。

このメソッドは、暗黙的に「前のタスクが完了したこと」をサーバーに通知する役割も担います。

#### タイムアウト設定

`request_task`メソッドは`timeout`引数を持ち、サーバーからの応答を待つ最大時間を秒単位で指定できます。デフォルトは**120秒**です。サーバーからの応答に時間がかかる場合（例：タスクの割り当て処理が重い、ネットワーク遅延など）、この値を調整することが推奨されます。

`request_task`は、サーバーの応答に応じて以下の結果を返します。

1.  **タスクが正常に割り当てられた場合**: タスク情報を含む`dict`（辞書）を返します。この辞書には、エージェントが実行すべきコマンドを含む`prompt`フィールドが含まれます。
2.  **割り当てるべきタスクがない場合**: `None`を返します。
3.  **サーバーへの接続に失敗した場合、またはタイムアウトした場合**: `None`を返し、エラーログが出力されます。

#### コード例

```python
import logging

# (クライアントの初期化は上記を参照)

try:
    logging.info(f"エージェント '{client.agent_id}' がタスクを要求します...")
    # タイムアウトを300秒に設定してタスクを要求
    task: dict | None = client.request_task(timeout=300)

    if task:
        print("新しいタスクが割り当てられました！")
        print(f"  実行プロンプト: {task.get('prompt')}")
        # ここにプロンプトを使ってコマンドを実行するロジックを実装
        # 例: subprocess.run(task.get('prompt'), shell=True)
        # ...

    else:
        print("現在、割り当て可能なタスクはありません。")

except Exception as e:
    # request_task内でrequests.exceptions.RequestExceptionは捕捉されるが、
    # 予期せぬエラーのために念のためハンドリング
    logging.error(f"予期せぬエラーが発生しました: {e}")

```

### 3.3. 戻り値のデータモデル

`request_task`が成功した場合に返される`dict`オブジェクトは、主に以下のキーを持ちます。

- `prompt` (str): エージェントが実行すべきコマンドを含むプロンプト
- `issue_url` (str): IssueへのリンクURL
- `labels` (list[str]): Issueに付与されているラベルのリスト
- `branch_name` (str): 作業用に作成されたブランチ名
