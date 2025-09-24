import datetime
import logging
import os
import subprocess
from typing import Any

import yaml


class GeminiExecutor:
    """
    Geminiモデルへのプロンプトを構築するクラス。
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
            logging.info(f"Attempting to open prompt file from CWD: {os.getcwd()}")
            with open(prompt_file, encoding="utf-8") as f:
                prompts = yaml.safe_load(f)
            self.build_prompt_template = prompts["prompt_template"]
        except (FileNotFoundError, KeyError) as e:
            logging.error(f"プロンプトファイルの読み込みまたは解析に失敗しました: {e}")
            # フォールバックとして空のテンプレートを設定
            self.build_prompt_template = ""







    def build_prompt(
        self, issue_id: int, title: str, body: str, branch_name: str
    ) -> str:
        """タスク実行のためのプロンプトを構築します。"""
        return self.build_prompt_template.format(
            issue_id=issue_id, title=title, body=body, branch_name=branch_name
        )
