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
        Executorを初期化します。

        Args:
            log_dir (Optional[str]): 実行ログを保存するディレクトリ。
            model (str): 使用するGeminiモデルの名前。
            prompt_file (str): プロンプトテンプレートが記述されたYAMLファイルのパス。
        """
        self.log_dir = log_dir
        self.model = model
        if self.log_dir:
            os.makedirs(self.log_dir, exist_ok=True)

        try:
            # prompt_fileが相対パスの場合、現在のファイルからの絶対パスに変換
            if not os.path.isabs(prompt_file):
                # prompt_fileが相対パスの場合、このファイルからの相対パスとして解決します
                filename = os.path.basename(prompt_file)
                prompt_file = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "prompts", filename)
                )
            logging.info(f"Attempting to open prompt file: {prompt_file}")
            with open(prompt_file, encoding="utf-8") as f:
                prompts = yaml.safe_load(f)
            self.build_prompt_template = prompts["prompt_template"].strip()
            self.review_fix_prompt_template = prompts["review_fix_prompt_template"].strip()
        except (FileNotFoundError, KeyError) as e:
            logging.error(f"プロンプトファイルの読み込みまたは解析に失敗しました: {e}")
            # フォールバックとして空のテンプレートを設定
            self.build_prompt_template = ""
            self.review_fix_prompt_template = ""

    def build_prompt(self, html_url: str, branch_name: str) -> str:
        """
        タスク情報に基づいて、エージェントが実行するためのプロンプトを構築します。

        Args:
            html_url (str): GitHub IssueのURL。
            branch_name (str): 作業用のブランチ名。

        Returns:
            str: 実行可能なコマンドを含むプロンプト文字列。
        """
        return self.build_prompt_template.format(
            html_url=html_url,
            branch_name=branch_name,
        )

    def build_code_review_prompt(self, pr_url: str, review_comment: str) -> str:
        """
        PR情報とレビューコメントに基づいて、コード修正のためのプロンプトを構築します。

        Args:
            pr_url (str): GitHub Pull RequestのURL。
            review_comment (str): レビューコメントの内容。

        Returns:
            str: コード修正のためのプロンプト文字列。
        """
        return self.review_fix_prompt_template.format(
            pr_url=pr_url,
            review_comment=review_comment,
        )
