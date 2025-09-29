import logging
import os
import re
import shutil
import subprocess
import time

from github_broker import AgentClient

# --- 待機時間設定 (秒) ---
SUCCESS_SLEEP_SECONDS = 5
NO_TASK_SLEEP_SECONDS = 30 * 60  # 30分
ERROR_SLEEP_SECONDS = 60 * 60  # 60分
# --------------------------

# --- ロギング設定 ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# --------------------


def main(run_once=False):
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

    # geminiコマンドの存在をチェック
    if not shutil.which("gemini"):
        logging.error(
            "'gemini' command not found. Please ensure it is installed and in your PATH."
        )
        return

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
                    logging.info("プロンプトを実行しています...")
                    try:
                        # promptを単一行に整形し、gemini cliに渡せるようにする
                        safe_prompt = re.sub(r"[\s\x00]+", " ", prompt).strip()
                        # context.mdにsafe_promptを書き込む
                        with open("context.md", "w", encoding="utf-8") as f:
                            f.write(safe_prompt)
                        # geminiコマンドを実行
                        command = (
                            "cat context.md | gemini --model gemini-2.5-flash --yolo"
                        )

                        result = subprocess.run(
                            command,
                            text=True,
                            capture_output=True,
                            check=True,
                            shell=True,
                        )
                        logging.info(f"gemini cli 実行結果 (stdout):\n{result.stdout}")
                        if result.stderr:
                            logging.warning(
                                f"gemini cli 実行結果 (stderr):\n{result.stderr}"
                            )
                    except subprocess.CalledProcessError as e:
                        logging.error(f"gemini cli の実行中にエラーが発生しました: {e}")
                        logging.error(f"stdout: {e.stdout}")
                        logging.error(f"stderr: {e.stderr}")
                else:
                    logging.warning(
                        "割り当てられたタスクにプロンプトが含まれていません。"
                    )

                logging.info("タスクの実行プロセスが完了しました。")
                if run_once:
                    break
                time.sleep(SUCCESS_SLEEP_SECONDS)  # 短い待機時間
            else:
                logging.info("利用可能なタスクがありません。30分後に再試行します。")
                if run_once:
                    break
                time.sleep(NO_TASK_SLEEP_SECONDS)  # 30分待機

        except Exception as e:
            logging.error(f"エラーが発生しました: {e}。60分後に再試行します...")
            if run_once:
                break
            time.sleep(ERROR_SLEEP_SECONDS)  # 60分待機


if __name__ == "__main__":
    main()
