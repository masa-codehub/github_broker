# `AgentClient` 利用ガイド

## 1. 概要

このドキュメントは、`github-broker`システムと連携する外部AIエージェントを開発するためのガイドです。提供される`AgentClient`クラスを利用することで、タスク割り当てサーバーとの通信を容易に実装できます。

`AgentClient`は、タスク割り当てサーバーに新しいタスクを要求するためのHTTPクライアントです。本アーキテクチャでは、クライアントはサーバーから渡されたプロンプトを実行するだけの「シンクライアント」としての役割を担います。

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

`request_task`メソッドを呼び出して、サーバーに新しいタスクを要求します。エージェントの情報は初期化時に渡しているため、このメソッドに引数は不要です。利用可能なタスクがない場合、サーバー側でタイムアウトまで待機するロングポーリングとして動作します。

このメソッドは、暗黙的に「前のタスクが完了したこと」をサーバーに通知する役割も担います。

#### タイムアウト設定

`request_task`メソッドは`timeout`引数を持ち、サーバーからの応答を待つ最大時間を秒単位で指定できます。デフォルトは**120秒**です。サーバーからの応答に時間がかかる場合（例：タスクの割り当て処理が重い、ネットワーク遅延など）、この値を調整することが推奨されます。

`request_task`は、サーバーの応答に応じて以下の結果を返します。

1.  **タスクが正常に割り当てられた場合**: タスク情報を含む`dict`（辞書）を返します。
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

    else:
        print("現在、割り当て可能なタスクはありません。")

except Exception as e:
    # request_task内でrequests.exceptions.RequestExceptionは捕捉されるが、
    # 予期せぬエラーのために念のためハンドリング
    logging.error(f"予期せぬエラーが発生しました: {e}")

```

### 3.3. 動的なタスク実行フロー (agents_main.py の例)

`agents_main.py` は、`AgentClient` を利用してタスク割り当てサーバーからタスクを取得し、そのタスクの内容に基づいて動的にコマンドを実行するエージェントの典型的な実装例です。このセクションでは、`agents_main.py` がどのようにタスクを実行し、コンテキストを更新するかを説明します。

#### 3.3.1. タスクの取得とプロンプトの実行

`agents_main.py` はループ内で `client.request_task()` を呼び出し、新しいタスクが割り当てられるのを待ちます。タスクが割り当てられると、そのタスクに含まれる `prompt` を利用して、以下のように `gemini` CLI ツールを実行します。

1.  **プロンプトの書き込み**: 割り当てられたタスクの `prompt` 内容を `context.md` というファイルに書き込みます。これにより、`gemini` CLI がこのファイルをコンテキストとして利用できるようになります。
2.  **`gemini` CLI の実行**: `cat context.md | gemini --model gemini-2.5-flash --yolo` コマンドを実行します。このコマンドは、`context.md` の内容を `gemini` CLI の標準入力に渡し、指定されたモデル (`gemini-2.5-flash`) と `yolo` オプション（確認なしで実行）で処理させます。
3.  **実行結果のログ出力**: `gemini` CLI の実行結果（標準出力と標準エラー出力）はログに出力され、エージェントの動作状況を把握できます。

#### 3.3.2. 環境変数による設定

`agents_main.py` は、以下の環境変数を使用してエージェントの動作を柔軟に設定できます。

-   `AGENT_NAME`: エージェントの識別名 (デフォルト: `sample-agent-001`)
-   `BROKER_HOST`: タスク割り当てサーバーのホスト名 (デフォルト: `localhost`)
-   `BROKER_PORT`: タスク割り当てサーバーのポート番号 (デフォルト: `8080`)
-   `AGENT_ROLE`: エージェントの役割 (デフォルト: `BACKENDCODER`)

これらの環境変数を設定することで、エージェントの接続先や役割を簡単に変更できます。

#### 3.3.3. 待機処理

`agents_main.py` は、タスクの状況に応じて適切な時間待機します。

-   **タスク成功時**: `SUCCESS_SLEEP_SECONDS` (5秒) 待機し、次のタスクリクエストを行います。
-   **タスクなし**: `NO_TASK_SLEEP_SECONDS` (1800秒 / 30分) 待機し、サーバーへの負荷を軽減します。
-   **エラー発生時**: `ERROR_SLEEP_SECONDS` (3600秒 / 60分) 待機し、一時的な問題からの回復を試みます。

### 3.4. 戻り値のデータモデル

`request_task`が成功した場合に返される`dict`オブジェクトは、主に以下のキーを持ちます。

- `issue_id` (int): GitHub Issueの番号
- `issue_url` (str): IssueへのリンクURL
- `title` (str): Issueのタイトル
- `body` (str | None): Issueの本文
- `labels` (list[str]): Issueに付与されているラベルのリスト
- `branch_name` (str): 作業用に作成されたブランチ名
- `prompt` (str): エージェントが実行すべきコマンドを含むプロンプト
