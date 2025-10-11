import asyncio
import logging
import os

import yaml


class GeminiExecutor:
    """
    サーバーサイドでAIエージェントに渡すためのプロンプトを生成するクラス。

    このクラスは、TaskServiceなどのアプリケーションサービスから呼び出され、
    与えられたタスク情報とプロンプトテンプレートを基に、
    最終的なプロンプト文字列を組み立てる責務を担います。

    実際のタスク実行は、このクラスが生成したプロンプトを受け取った
    クライアント側のエージェントが行います。
    """

    def __init__(
        self,
        log_dir: str | None = None,
        model: str = "gemini-1.5-flash",
        prompt_file: str = "github_broker/infrastructure/prompts/gemini_executor.yml",
    ):
        """
        Initializes the Executor.

        Args:
            log_dir (Optional[str]): Directory to save execution logs.
            model (str): Name of the Gemini model to use.
            prompt_file (str): Path to the YAML file containing prompt templates.
        """
        self.log_dir = log_dir
        self.model = model
        if self.log_dir:
            os.makedirs(self.log_dir, exist_ok=True)

        self.build_prompt_template = ""
        self.review_fix_prompt_template = ""

        try:
            if not os.path.isabs(prompt_file):
                filename = os.path.basename(prompt_file)
                prompt_file = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "prompts", filename)
                )
            logging.info(f"Attempting to open prompt file: {prompt_file}")
            with open(prompt_file, encoding="utf-8") as f:
                prompts = yaml.safe_load(f)

            if prompts and isinstance(prompts, dict):
                prompt_definitions = {
                    "prompt_template": "build_prompt_template",
                    "review_fix_prompt_template": "review_fix_prompt_template",
                }
                for key, attr_name in prompt_definitions.items():
                    template = prompts.get(key, "").strip()
                    setattr(self, attr_name, template)
                    if not template:
                        logging.warning(
                            f"'{key}' not found or empty in the YAML file. Using an empty template."
                        )
            else:
                logging.error(
                    "YAML file is empty or not in the expected format. Using empty templates."
                )

        except FileNotFoundError as e:
            logging.error(f"Prompt file not found: {e}")

    def build_prompt(
        self,
        html_url: str,
        branch_name: str,
        pr_url: str | None = None,
        review_comments: list[str] | None = None,
    ) -> str:
        """
        タスク情報に基づいて、エージェントが実行するためのプロンプトを構築します。

        Args:
            html_url (str): GitHub IssueのURL。
            branch_name (str): 作業用のブランチ名。
            pr_url (Optional[str]): GitHub Pull RequestのURL。
            review_comments (Optional[list[str]]): レビューコメントのリスト。

        Returns:
            str: 実行可能なコマンドを含むプロンプト文字列。
        """
        formatted_comments = "\n".join(review_comments) if review_comments else "N/A"
        return self.build_prompt_template.format(
            html_url=html_url,
            branch_name=branch_name,
            pr_url=pr_url if pr_url else "N/A",
            review_comments=formatted_comments,
        )

    def build_code_review_prompt(self, pr_url: str, review_comments: list[str]) -> str:
        """
        PR情報とレビューコメントに基づいて、コード修正のためのプロンプトを構築します。

        Args:
            pr_url (str): GitHub Pull RequestのURL。
            review_comments (list[str]): レビューコメントのリスト。

        Returns:
            str: コード修正のためのプロンプト文字列。
        """
        formatted_comments = "\n".join(review_comments) if review_comments else "N/A"
        return self.review_fix_prompt_template.format(
            pr_url=pr_url,
            review_comments=formatted_comments,
        )

    async def execute(
        self, issue_id: int, html_url: str, branch_name: str, prompt: str
    ) -> str:
        """
        指定されたプロンプトを実行し、結果を返します。
        NOTE: これはmypyエラーをパスさせるためのダミー実装です。
        """
        logging.info(f"Executing prompt for issue {issue_id}...")
        # 現時点ではAPIを呼び出さずにダミーレスポンスを返す
        await asyncio.sleep(0)  # asyncメソッドであることを示すため
        return "dummy response from executor"
