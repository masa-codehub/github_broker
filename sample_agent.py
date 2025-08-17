import json
import time
import sys
import os
import subprocess
import logging

from github_broker.infrastructure.agent.client import AgentClient
from github_broker.infrastructure.executors.gemini_executor import GeminiCliExecutor

# --- ロギング設定 ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
# --------------------


if __name__ == "__main__":
    # --- エージェントの設定 ---
    # AGENT_IDはコンテナ実行時に環境変数で上書きされることを想定
    agent_id = os.getenv("AGENT_ID", "gemini-agent")
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
    logging.info(f"Capabilities: {capabilities}")
    print("-" * 30)

    # AgentClientとExecutorを初期化
    client = AgentClient(agent_id=agent_id, capabilities=capabilities)
    executor = GeminiCliExecutor()

    while True:
        logging.info("Requesting a new task from the server...")
        # 次のタスクを要求することで、前のタスクが完了したことをサーバーに通知
        assigned_task = client.request_task()

        if assigned_task:
            executor.execute(assigned_task)
            logging.info("Proceeding to the next task...")
            time.sleep(5)  # 短い待機時間
        else:
            logging.info("No more tasks available. Shutting down the agent.")
            break
