import json
import logging
import os
import shlex
import subprocess
from typing import Any

import requests

from github_broker.application.exceptions import PromptExecutionError


class AgentClient:
    """
    GitHubタスクブローカーサーバーと対話するためのクライアント。
    """

    def __init__(
        self,
        agent_id: str,
        agent_role: str,
        host: str = "localhost",
        port: int | None = None,
    ):
        """
        AgentClientを初期化します。

        Args:
            agent_id (str): エージェントの一意な識別子。
            agent_role (str): エージェントのロール。
            host (str): サーバーのホスト名。デフォルトは"localhost"。
            port (Optional[int]): サーバーのポート。デフォルトはAPP_PORT環境変数または8080。
        """
        self.agent_id = agent_id
        self.agent_role = agent_role
        self.host = host
        self.port = port if port is not None else int(os.getenv("BROKER_PORT", 8080))
        self.endpoint = "/request-task"
        self.headers = {"Content-Type": "application/json"}

    def request_task(self, timeout: int = 120) -> dict[str, Any] | None:
        """
        GitHubタスクブローカーサーバーに新しいタスクをリクエストします。
        これは、以前のタスクが完了したことをサーバーに暗黙的に通知します。

        Args:
            timeout (int): リクエストのタイムアウト（秒）。デフォルトは120秒。

        Returns:
            Optional[Dict[str, Any]]: 割り当てられたタスク情報、または利用可能なタスクがない場合はNone。

        Raises:
            PromptExecutionError: サーバーから受け取ったプロンプトの実行に失敗した場合。
        """
        payload = {"agent_id": self.agent_id, "agent_role": self.agent_role}
        url = f"http://{self.host}:{self.port}{self.endpoint}"
        try:
            response = requests.post(
                url, json=payload, headers=self.headers, timeout=timeout
            )

            logging.info(f"Server response: {response.status_code} {response.reason}")

            if response.status_code == 204:
                logging.info("No assignable tasks available at the moment.")
                return None

            response.raise_for_status()

            task = response.json()
            logging.info("New task assigned:")
            logging.info(json.dumps(task, indent=2, ensure_ascii=False))

            if "prompt" in task and task["prompt"]:
                # Define an allowlist of permitted commands
                allowed_commands = [
                    "echo",
                    "ls",
                    "pwd",
                    # Add other safe commands as needed
                ]
                try:
                    prompt_args = shlex.split(task["prompt"])
                    if prompt_args and prompt_args[0] in allowed_commands:
                        logging.info(f"Executing prompt: {task['prompt']}")
                        subprocess.run(
                            prompt_args,
                            check=True,
                            text=True,
                            capture_output=True,
                            timeout=timeout,
                        )
                        logging.info("Prompt executed successfully.")
                    else:
                        logging.error(
                            f"Prompt '{task['prompt']}' is not in the allowlist and will not be executed."
                        )
                        raise PromptExecutionError(
                            f"Prompt '{task['prompt']}' is not allowed."
                        )
                except subprocess.CalledProcessError as e:
                    error_message = (
                        f"Prompt execution failed. {e}. Stderr: {e.stderr.strip()}"
                    )
                    logging.error(error_message)
                    raise PromptExecutionError(error_message) from e
            return task

        except requests.exceptions.RequestException as e:
            logging.error(f"Error connecting to the server at {url}: {e}")
            return None
