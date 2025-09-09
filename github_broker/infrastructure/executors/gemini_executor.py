import datetime
import logging
import os
import subprocess
from typing import Any

import yaml


class GeminiExecutor:
    """
    'gemini'コマンドラインツールを使用してタスクを実行するExecutor。
    品質向上のため、実行とレビューの2段階プロセスを実装しています。
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
            with open(prompt_file, encoding="utf-8") as f:
                prompts = yaml.safe_load(f)
            self.build_prompt_template = prompts["build_prompt"]
            self.review_prompt_template = prompts["review_prompt"]
        except (FileNotFoundError, KeyError) as e:
            logging.error(f"プロンプトファイルの読み込みまたは解析に失敗しました: {e}")
            # フォールバックとして空のテンプレートを設定
            self.build_prompt_template = ""
            self.review_prompt_template = ""

    def execute(self, task: dict[str, Any]):
        """タスクを初回実行と自己レビューの2段階プロセスで実行します。

        Args:
            task (Dict[str, Any]): タスクの詳細を含む辞書。
        """
        # --- フェーズ1: 初回実行 ---
        logging.info("フェーズ1: 初回実行を開始します...")
        issue_title = task.get("title", "")
        issue_body = task.get("body", "")
        branch_name = task.get("branch_name", "")

        initial_prompt = self._build_prompt(issue_title, issue_body, branch_name)
        command = ["gemini", "--yolo", "-m", self.model, "-p", initial_prompt]

        log_filepath = self._get_log_filepath(task.get("agent_id"))

        success = self._run_sub_process(command, log_filepath)

        if not success or not log_filepath:
            logging.error(
                "初回実行に失敗したか、ロギングが無効です。レビューステップをスキップします。"
            )
            return

        # --- フェーズ2: レビューと修正 ---
        logging.info("フェーズ2: レビューと修正を開始します...")
        try:
            with open(log_filepath, encoding="utf-8") as f:
                initial_output = f.read()
        except Exception as e:
            logging.error(
                f"レビューのためにログファイルを読み込めませんでした: {e}。レビューステップをスキップします。"
            )
            return

        review_prompt = self._build_review_prompt(initial_prompt, initial_output)
        review_command = ["gemini", "--yolo", "-m", self.model, "-p", review_prompt]

        # レビューフェーズのヘッダーをログファイルに追記
        with open(log_filepath, "a", encoding="utf-8") as f:
            f.write("\n\n---\n\n# フェーズ2: レビューと修正\n\n")
            f.write(
                f"モデルに送信されたレビュープロンプト:\n```\n{review_prompt}\n```\n\n**最終成果物:**\n"
            )

        self._run_sub_process(review_command, log_filepath)
        logging.info("レビューと修正フェーズが完了しました。")

    def _run_sub_process(self, command: list[str], log_filepath: str | None) -> bool:
        """コマンドをサブプロセスとして実行し、その出力を指定されたファイルに記録します。"""
        try:
            logging.info(f"コマンドを実行します: {' '.join(command)}")
            if log_filepath:
                with open(log_filepath, "a", encoding="utf-8") as log_file:
                    with subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                    ) as proc:
                        if proc.stdout:
                            for line in proc.stdout:
                                logging.info(line.strip())
                                log_file.write(line)
                    return proc.returncode == 0
            else:
                with subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                ) as proc:
                    if proc.stdout:
                        for line in proc.stdout:
                            logging.info(line.strip())
                return proc.returncode == 0

        except FileNotFoundError:
            logging.error(
                "エラー: 'gemini'コマンドが見つかりません。gemini-cliがインストールされ、PATHに含まれていることを確認してください。"
            )
            return False
        except Exception as e:
            logging.error(f"'gemini cli'の実行中に予期せぬエラーが発生しました: {e}")
            return False

    def _get_log_filepath(self, agent_id: str | None) -> str | None:
        """ロギングが有効でagent_idが存在する場合に、ログファイルのパスを構築します。"""
        if not self.log_dir:
            return None
        if not agent_id:
            logging.warning(
                "taskに'agent_id'が見つかりません。ログファイルを作成できません。"
            )
            return None

        timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        filename = f"{agent_id}_{timestamp}.md"
        filepath = os.path.join(self.log_dir, filename)
        logging.info(f"コマンドの出力を次のファイルに記録します: {filepath}")
        return filepath

    def _build_prompt(self, title: str, body: str, branch_name: str) -> str:
        """タスク実行のための初回プロンプトを構築します。"""
        return self.build_prompt_template.format(
            title=title, body=body, branch_name=branch_name
        )

    def _build_review_prompt(self, original_prompt: str, execution_output: str) -> str:
        """自己レビューステップのためのプロンプトを構築します。"""
        return self.review_prompt_template.format(
            original_prompt=original_prompt, execution_output=execution_output
        )
