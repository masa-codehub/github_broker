import logging
import os
import time

from github_broker import AgentClient, GeminiExecutor

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

    gemini_log_dir = os.getenv("MESSAGE_DIR", "/app/logs")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    agent_role = os.getenv("AGENT_ROLE", "BACKENDCODER")
    # --------------------------

    logging.info(f"エージェント '{agent_id}' を開始します。")
    logging.info(f"サーバー {host}:{port} に接続しています。")
    logging.info(f"ログディレクトリ: {gemini_log_dir}")
    logging.info(f"ロール: {agent_role}")
    logging.info("-" * 30)

    # AgentClientとExecutorを初期化
    client = AgentClient(agent_id=agent_id, agent_role=agent_role, host=host, port=port)
    executor = GeminiExecutor(log_dir=gemini_log_dir, model=gemini_model)

    while True:
        try:
            logging.info("サーバーに新しいタスクをリクエストしています...")
            # agent_idとcapabilitiesは初期化時に渡しているため、引数は不要
            assigned_task = client.request_task()

            if assigned_task:
                logging.info(
                    f"新しいタスクが割り当てられました: #{assigned_task.get('issue_id')} - {assigned_task.get('title')}"
                )

                # ログファイル名のためにagent_idをタスク辞書に追加
                assigned_task["agent_id"] = agent_id

                executor.execute(assigned_task)
                logging.info("タスクの実行プロセスが完了しました。")
                time.sleep(5)  # 短い待機時間
            else:
                logging.info("利用可能なタスクがありません。30分後に再試行します。")
                time.sleep(30 * 60)  # 30分待機

        except Exception as e:
            logging.error(f"エラーが発生しました: {e}。60分後に再試行します...")
            time.sleep(60 * 60)  # 60分待機
