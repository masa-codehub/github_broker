import datetime
import logging
import os
import subprocess
from typing import Any


class GeminiExecutor:
    """
    'gemini'コマンドラインツールを使用してタスクを実行するExecutor。
    品質向上のため、実行とレビューの2段階プロセスを実装しています。
    """

    def __init__(self, log_dir: str | None = None, model: str = "gemini-2.5-flash"):
        """
        Executorを初期化します。

        Args:
            log_dir (Optional[str]): 実行ログを保存するディレクトリ。
            model (str): 使用するGeminiモデルの名前。
        """
        self.log_dir = log_dir
        self.model = model
        if self.log_dir:
            os.makedirs(self.log_dir, exist_ok=True)

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
            log_file = (
                open(log_filepath, "a", encoding="utf-8") if log_filepath else None
            )

            try:
                with subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                ) as proc:
                    for line in proc.stdout:
                        if log_file:
                            log_file.write(line)
                return proc.returncode == 0
            finally:
                if log_file:
                    log_file.close()

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
        return (
            f"以下のGitHub Issueを解決してください。\n"
            f"作業用のブランチ '{branch_name}' は既に作成済みです。\n"
            f"まずそのブランチに切り替えてから、Issueの指示に従って実装を開始してください。\n\n"
            f"# Issue: {title}\n\n{body}"
        )

    def _build_review_prompt(self, original_prompt: str, execution_output: str) -> str:
        """自己レビューステップのためのプロンプトを構築します。"""
        return (
            f"あなたはシニア品質保証エンジニアです。あなたのタスクは、開発者エージェントの作業をレビューすることです。\n"
            f"以下に元の指示と、その指示に対するエージェントの出力が示されています。\n"
            f"エージェントの出力が、元の指示を完全かつ正確に実装しているか確認してください。間違い、漏れ、改善の余地がある点を特定してください。\n"
            f"その上で、修正および完成させた最終版の成果物全体を提示してください。あなたの出力は、修正点だけではなく、最終的な完成物そのものである必要があります。\n\n"
            f"--- 元の指示 ---\n{original_prompt}\n\n"
            f"--- エージェントの初回出力 ---\n{execution_output}"
        )
