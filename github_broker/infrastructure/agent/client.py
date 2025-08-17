import json
import os
import logging
from typing import Dict, Any, Optional, List
import requests

class AgentClient:
    """
    A client for interacting with the GitHub Task Broker server.
    """

    def __init__(self, agent_id: str, capabilities: List[str], host: str = "localhost", port: Optional[int] = None):
        """
        Initializes the AgentClient.

        Args:
            agent_id (str): The unique identifier for the agent.
            capabilities (List[str]): The list of capabilities of the agent.
            host (str): The hostname of the server. Defaults to "localhost".
            port (Optional[int]): The port of the server. Defaults to APP_PORT env var or 8080.
        """
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.host = host
        self.port = port if port is not None else int(os.getenv("APP_PORT", 8080))
        self.endpoint = "/api/v1/request-task"
        self.headers = {"Content-Type": "application/json"}

    def request_task(self) -> Optional[Dict[str, Any]]:
        """
        Requests a new task from the GitHub Task Broker server.
        This also implicitly notifies the server that the previous task is complete.

        Returns:
            Optional[Dict[str, Any]]: The assigned task information, or None if no task is available.
        """
        payload = {
            "agent_id": self.agent_id,
            "capabilities": self.capabilities
        }
        url = f"http://{self.host}:{self.port}{self.endpoint}"
        try:
            # `requests`ライブラリは、接続プールやタイムアウト管理などを自動で行います。
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)

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
