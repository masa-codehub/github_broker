import json
import http.client
import time
import sys
import os
import subprocess


def request_task(agent_id: str, capabilities: list[str]):
    """
    GitHubタスクブローカーサーバーにタスクを要求する関数。
    (このサンプルは、自身もDockerコンテナとして実行されることを想定しています)

    Args:
        agent_id (str): エージェントを一位に識別するためのID。
        capabilities (list[str]): エージェントが持つ能力のリスト (例: ["python", "docker"])。

    Returns:
        dict or None: 割り当てられたタスク情報。タスクがない場合はNone。
    """
    # --- 接続先サーバーの設定 ---
    # 同じコンテナ内でサーバーとエージェントを実行するため、ホスト名は'localhost'になります。
    host = "localhost"
    # 環境変数 `APP_PORT` からポート番号を読み込む。指定がなければデフォルトで8080を使用。
    port = int(os.getenv("APP_PORT", 8080))
    # ------------------------------------

    endpoint = "/api/v1/request-task"

    # サーバーに送信するデータ（ペイロード）
    payload = {
        "agent_id": agent_id,
        "capabilities": capabilities
    }
    # HTTPヘッダー
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # サーバーとの接続を確立
        conn = http.client.HTTPConnection(host, port)
        # POSTリクエストを送信
        conn.request("POST", endpoint, body=json.dumps(
            payload), headers=headers)
        # サーバーからのレスポンスを取得
        response = conn.getresponse()

        # レスポンスのステータスコードと理由を表示
        print(f"サーバーからの応答: {response.status} {response.reason}")

        # ステータスコードに応じた処理
        if response.status == 200:  # 成功
            response_data = response.read().decode('utf-8')
            task = json.loads(response_data)
            print("新しいタスクが割り当てられました:")
            print(json.dumps(task, indent=2, ensure_ascii=False))
            return task
        elif response.status == 204:  # No Content
            print("現時点で割り当て可能なタスクはありませんでした。")
            return None
        else:  # その他のエラーステータス
            error_data = response.read().decode('utf-8')
            print(f"エラーが発生しました: {error_data}")
            return None

    except Exception as e:
        # コンテナ環境では、接続拒否よりも名前解決エラーなどが先に発生する可能性がある
        print(f"エラー: サーバー({host}:{port})への接続中にエラーが発生しました。")
        print(f"詳細: {e}")
        return None
    finally:
        # 接続が確立されていれば、必ず閉じる
        if 'conn' in locals():
            conn.close()


# このスクリプトが直接実行された場合に以下のコードが実行される
if __name__ == "__main__":
    # このエージェントのIDと能力を定義
    # コンテナ実行時に環境変数で上書きされることを想定
    my_agent_id = os.getenv("AGENT_ID", "gemini-agent")
    my_capabilities = [
        "software-design",
        "clean-architecture",
        "tdd",
        "refactoring",
        "python",
        "fastapi",
        "docker",
        "github-actions",
        "technical-writing",
        "日本語"
    ]

    print(f"エージェント '{my_agent_id}' を起動します。")
    print(f"能力: {my_capabilities}")
    print("-" * 30)

    # タスクがなくなるまでループ処理を続ける
    while True:
        print("\n新しいタスクをサーバーに要求します...")
        # 次のタスクを要求することで、前のタスクが完了したことをサーバーに通知します
        assigned_task = request_task(my_agent_id, my_capabilities)

        if assigned_task:
            print("\n割り当てられたタスクを 'gemini cli' に渡して処理を開始します...")

            # Issueの情報をプロンプトとして整形
            issue_title = assigned_task.get("title", "")
            issue_body = assigned_task.get("body", "")
            branch_name = assigned_task.get("branch_name", "")

            prompt = (
                f"以下のGitHub Issueを解決してください。\n"
                f"作業用のブランチは既に '{branch_name}' という名前で作成済みです。\n"
                f"まず、そのブランチに切り替えてから、Issueの指示に従って実装を開始してください。\n\n"
                f"# Issue: {issue_title}\n\n{issue_body}"
            )

            try:
                # 'gemini' コマンドを非対話モードで実行
                command = ["gemini", "--yolo", "-p", prompt]
                print(f"実行コマンド: {" ".join(command)}")

                # subprocess.runを使ってコマンドを実行し、出力をリアルタイムで表示
                with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
                    for line in proc.stdout:
                        print(line, end='')

                if proc.returncode == 0:
                    print("\n'gemini cli' によるタスク処理が正常に完了しました。")
                else:
                    print(
                        f"\n'gemini cli' の実行中にエラーが発生しました。(終了コード: {proc.returncode})")

            except FileNotFoundError:
                print(
                    "\nエラー: 'gemini' コマンドが見つかりません。gemini-cliがインストールされ、PATHが通っているか確認してください。")
            except Exception as e:
                print(f"\n'gemini cli' の実行中に予期せぬエラーが発生しました: {e}")

            print("\n次のタスクに進みます...")
            time.sleep(5)  # サーバーへの連続リクエストを防ぐための短い待機

        else:
            print("\n割り当て可能なタスクがなくなったため、エージェントを終了します。")
            break  # ループを抜ける
