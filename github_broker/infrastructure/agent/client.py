import json
import logging
import os
from typing import Any

import requests


class AgentClient:
    """
    GitHubタスクブローカーサーバーと対話するためのクライアント。
    """

    def __init__(
        self,
        agent_id: str,
        capabilities: list[str],
        host: str = "localhost",
        port: int | None = None,
    ):
        """
        AgentClientを初期化します。

        Args:
            agent_id (str): エージェントの一意な識別子。
            capabilities (List[str]): エージェントの機能リスト。
            host (str): サーバーのホスト名。デフォルトは"localhost"。
            port (Optional[int]): サーバーのポート。デフォルトはAPP_PORT環境変数または8080。
        """
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.host = host
        self.port = port if port is not None else int(os.getenv("BROKER_PORT", 8080))
        self.endpoint = "/request-task"
        self.headers = {"Content-Type": "application/json"}

    def request_task(self) -> dict[str, Any] | None:
        """
        GitHubタスクブローカーサーバーに新しいタスクをリクエストします。
        これは、以前のタスクが完了したことをサーバーに暗黙的に通知します。

        Returns:
            Optional[Dict[str, Any]]: 割り当てられたタスク情報、または利用可能なタスクがない場合はNone。
        """
        payload = {"agent_id": self.agent_id, "capabilities": self.capabilities}
        url = f"http://{self.host}:{self.port}{self.endpoint}"
        try:
            # `requests`ライブラリは、接続プールやタイムアウト管理などを自動で行います。
            response = requests.post(
                url, json=payload, headers=self.headers, timeout=30
            )

            logging.info(f"Server response: {response.status_code} {response.reason}")

            if response.status_code == 204:
                logging.info("No assignable tasks available at the moment.")
                return None

            # 200番台以外のステータスコードの場合に例外を発生させ、一括でエラーハンドリングします。
            response.raise_for_status()

            # 200 OKの場合
            task = response.json()
            logging.info("New task assigned:")
            logging.info(json.dumps(task, indent=2, ensure_ascii=False))
            return task

        except requests.exceptions.RequestException as e:
            logging.error(f"Error connecting to the server at {url}: {e}")
            return None
