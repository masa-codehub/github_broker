import json
import http.client
import os
import logging
from typing import Dict, Any, Optional, List

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
        conn = None
        try:
            conn = http.client.HTTPConnection(self.host, self.port)
            conn.request("POST", self.endpoint, body=json.dumps(payload), headers=self.headers)
            response = conn.getresponse()

            logging.info(f"Server response: {response.status} {response.reason}")

            if response.status == 200:
                response_data = response.read().decode('utf-8')
                task = json.loads(response_data)
                logging.info("New task assigned:")
                logging.info(json.dumps(task, indent=2, ensure_ascii=False))
                return task
            elif response.status == 204:
                logging.info("No assignable tasks available at the moment.")
                return None
            else:
                error_data = response.read().decode('utf-8')
                logging.error(f"An error occurred: {error_data}")
                return None

        except Exception as e:
            logging.error(f"Error connecting to the server at {self.host}:{self.port}: {e}")
            return None
        finally:
            if conn:
                conn.close()
