import json
import time
import sys
import os
import subprocess
import logging

from github_broker import AgentClient, GeminiExecutor

# --- ロギング設定 ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
# --------------------


if __name__ == "__main__":
    # --- エージェントの設定 ---
    agent_id = os.getenv("AGENT_ID", "sample-agent-001")
    # AgentClientとmain.pyの仕様に合わせ、hostとportで接続先を指定
    host = os.getenv("SERVER_HOST", "localhost")
    port = int(os.getenv("APP_PORT", 8080))

    gemini_log_dir = os.getenv("GEMINI_LOG_DIR", "/app/logs")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

    capabilities = [
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
    # --------------------------

    logging.info(f"Starting agent '{agent_id}'.")
    logging.info(f"Connecting to server at {host}:{port}")
    logging.info(f"Log Directory: {gemini_log_dir}")
    logging.info(f"Capabilities: {capabilities}")
    print("-" * 30)

    # AgentClientとExecutorを初期化
    client = AgentClient(
        agent_id=agent_id, capabilities=capabilities, host=host, port=port)
    executor = GeminiExecutor(log_dir=gemini_log_dir, model=gemini_model)

    while True:
        try:
            logging.info("Requesting a new task from the server...")
            # agent_idとcapabilitiesは初期化時に渡しているため、引数は不要
            assigned_task = client.request_task()

            if assigned_task:
                logging.info(
                    f"New task assigned: #{assigned_task.get('issue_id')} - {assigned_task.get('title')}")

                # ログファイル名のためにagent_idをタスク辞書に追加
                assigned_task['agent_id'] = agent_id

                executor.execute(assigned_task)
                logging.info("Task execution process finished.")
                time.sleep(5)  # 短い待機時間
            else:
                logging.info(
                    "No task available. Waiting for 30 seconds before retrying.")
                time.sleep(30)
                break

        except Exception as e:
            logging.error(f"An error occurred: {e}. Retrying in 60 seconds...")
            time.sleep(60)
