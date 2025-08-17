import subprocess
import logging
from typing import Dict, Any

class GeminiCliExecutor:
    """
    An executor responsible for running tasks using the 'gemini' command-line tool.
    """

    def execute(self, task: Dict[str, Any]):
        """Executes the given task by invoking the 'gemini cli'.

        Args:
            task (Dict[str, Any]): A dictionary containing task details like title, body, and branch_name.
        """
        logging.info("Passing the assigned task to 'gemini cli' to start processing...")

        issue_title = task.get("title", "")
        issue_body = task.get("body", "")
        branch_name = task.get("branch_name", "")

        prompt = self._build_prompt(issue_title, issue_body, branch_name)

        try:
            command = ["gemini", "--yolo", "-p", prompt]
            logging.info(f"Executing command: {' '.join(command)}")

            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
                for line in proc.stdout:
                    print(line, end='')

            if proc.returncode == 0:
                logging.info("'gemini cli' task processing completed successfully.")
            else:
                logging.error(f"'gemini cli' execution failed with exit code: {proc.returncode}")

        except FileNotFoundError:
            logging.error("Error: 'gemini' command not found. Please ensure gemini-cli is installed and in your PATH.")
        except Exception as e:
            logging.error(f"An unexpected error occurred while executing 'gemini cli': {e}")

    def _build_prompt(self, title: str, body: str, branch_name: str) -> str:
        """
        gemini CLI用のプロンプトを構築します。
        
        プロンプトは、GitHub Issueの解決を依頼する内容となっており、作業用ブランチ名、Issueタイトル、Issue本文を含めて構成されます。
        まず指定されたブランチに切り替え、その後Issueの指示に従って実装を開始するよう促します。
        
        Args:
            title (str): GitHub Issueのタイトル。
            body (str): GitHub Issueの本文。
            branch_name (str): 既に作成済みの作業用ブランチ名。
        
        Returns:
            str: gemini CLIに渡すためのプロンプト文字列。
        """
        return (
            f"Please resolve the following GitHub Issue.\n"
            f"A working branch named '{branch_name}' has already been created for you.\n"
            f"First, switch to that branch, then start implementation according to the Issue's instructions.\n\n"
            f"# Issue: {title}\n\n{body}"
        )