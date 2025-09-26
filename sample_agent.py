import logging
import os
import shlex
import subprocess
import time

from github_broker import AgentClient

# --- ロギング設定 ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# --------------------


if __name__ == "__main__":
    # --- エージェントの設定 ---
    agent_id = os.getenv("AGENT_NAME", "sample-agent-001")
    # AgentClientとmain.pyの仕様に合わせ、hostとportで接続先を指定
    host = os.getenv("BROKER_HOST", "localhost")
    port = int(os.getenv("BROKER_PORT", 8080))

    agent_role = os.getenv("AGENT_ROLE", "BACKENDCODER")
    # --------------------------

    logging.info(f"エージェント '{agent_id}' を開始します。")
    logging.info(f"サーバー {host}:{port} に接続しています。")
    logging.info(f"ロール: {agent_role}")
    logging.info("-" * 30)

    # AgentClientを初期化
    client = AgentClient(agent_id=agent_id, agent_role=agent_role, host=host, port=port)

    while True:
        try:
            logging.info("サーバーに新しいタスクをリクエストしています...")
            # agent_idとcapabilitiesは初期化時に渡しているため、引数は不要
            assigned_task = client.request_task()

            if assigned_task:
                logging.info(
                    f"新しいタスクが割り当てられました: #{assigned_task.get('issue_id')} - {assigned_task.get('title')}"
                )

                prompt = assigned_task.get("prompt")
                if prompt:
                    # SECURITY WARNING:
                    # The following code executes the 'prompt' string as a shell command.
                    # It uses shlex.split() to safely parse the command and avoid shell injection vulnerabilities.
                    # However, the command itself comes from a remote server and could be arbitrary.
                    # This code assumes that the 'prompt' comes from a trusted source.
                    # DO NOT use this pattern with untrusted input.
                    logging.info("プロンプトを実行しています...")
                    try:
                        result = subprocess.run(
                            shlex.split(prompt),
                            text=True,
                            capture_output=True,
                            check=True,
                        )
                        logging.info(f"プロンプト実行結果 (stdout):\n{result.stdout}")
                        if result.stderr:
                            logging.warning(
                                f"プロンプト実行結果 (stderr):\n{result.stderr}"
                            )
                    except subprocess.CalledProcessError as e:
                        logging.error(f"プロンプトの実行中にエラーが発生しました: {e}")
                        logging.error(f"stdout: {e.stdout}")
                        logging.error(f"stderr: {e.stderr}")
                else:
                    logging.warning(
                        "割り当てられたタスクにプロンプトが含まれていません。"
                    )

                logging.info("タスクの実行プロセスが完了しました。")
                time.sleep(5)  # 短い待機時間
            else:
                logging.info("利用可能なタスクがありません。30分後に再試行します。")
                time.sleep(30 * 60)  # 30分待機

        except Exception as e:
            logging.error(f"エラーが発生しました: {e}。60分後に再試行します...")
            time.sleep(60 * 60)  # 60分待機
