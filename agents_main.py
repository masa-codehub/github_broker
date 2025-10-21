import logging
import os
import re
import subprocess
import time

from github_broker import AgentClient

# --- 待機時間設定 (秒) ---
SUCCESS_SLEEP_SECONDS = 5
NO_TASK_SLEEP_SECONDS = 5 * 60  # 5分
ERROR_SLEEP_SECONDS = 10 * 60  # 10分
CONTEXT_UPDATE_TIMEOUT_SECONDS = 300  # 5分
# --------------------------

# --- ロギング設定 ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# --------------------

# --- デフォルト値 ---
DEFAULT_TASK_TYPE = "development"
DEFAULT_REQUIRED_ROLE = "BACKENDCODER"
# --------------------

# --- Geminiモデル設定 ---
GEMINI_MODEL_MAP = {
    "review": "gemini-2.5-pro",
}
DEFAULT_GEMINI_MODEL = "gemini-flash-latest"
# --------------------------


def _handle_subprocess_error(e: subprocess.CalledProcessError, run_once: bool) -> bool:
    """Subprocess実行時のエラーをハンドリングし、リトライするかどうかを決定する。"""
    logging.error(f"コマンド '{e.cmd}' の実行中にエラーが発生しました: {e}")
    if e.stdout:
        logging.error(f"stdout: {e.stdout}")
    if e.stderr:
        logging.error(f"stderr: {e.stderr}")

    if run_once:
        return False  # break

    logging.info(f"{ERROR_SLEEP_SECONDS}秒待機して、次のタスクリクエストに進みます。")
    time.sleep(ERROR_SLEEP_SECONDS)
    return True  # continue


def main(run_once=False):
    # --- エージェントの設定 ---
    agent_id = os.getenv("AGENT_NAME", "sample-agent-001")
    host = os.getenv("BROKER_HOST", "localhost")
    port = int(os.getenv("BROKER_PORT", 8080))

    client = AgentClient(agent_id=agent_id, host=host, port=port)

    while True:
        try:
            logging.info("サーバーに新しいタスクをリクエストしています...")
            assigned_task = client.request_task()

            if assigned_task:
                logging.info(
                    f"新しいタスクが割り当てられました: #{assigned_task.get('issue_id')} - {assigned_task.get('title')}"
                )

                prompt = assigned_task.get("prompt")
                if prompt:
                    task_type = assigned_task.get("task_type", DEFAULT_TASK_TYPE)
                    required_role = assigned_task.get(
                        "required_role", DEFAULT_REQUIRED_ROLE
                    )

                    gemini_model = GEMINI_MODEL_MAP.get(task_type, DEFAULT_GEMINI_MODEL)

                    logging.info(
                        f"タスクタイプ: {task_type}, 必須ロール: {required_role}, 使用モデル: {gemini_model}"
                    )

                    try:
                        # 1. コンテキスト更新
                        logging.info("コンテキスト更新スクリプトを実行しています...")
                        env = os.environ.copy()
                        env["AGENT_ROLE"] = required_role
                        result = subprocess.run(
                            ["bash", "/app/.build/update_gemini_context.sh"],
                            text=True,
                            check=True,
                            capture_output=True,
                            env=env,
                            timeout=CONTEXT_UPDATE_TIMEOUT_SECONDS,
                        )
                        logging.info("コンテキスト更新完了。")
                        if result.stdout:
                            logging.info(
                                f"コンテキスト更新スクリプトの出力:\n{result.stdout}"
                            )
                        if result.stderr:
                            logging.warning(
                                f"コンテキスト更新スクリプトのエラー出力:\n{result.stderr}"
                            )

                        # 2. プロンプトの書き込み
                        safe_prompt = re.sub(r"[\x00]+", "", prompt).strip()
                        with open("context.md", "w", encoding="utf-8") as f:
                            f.write(safe_prompt)

                        # 3. geminiコマンドの実行
                        command = (
                            f"cat context.md | gemini --model {gemini_model} --yolo"
                        )
                        logging.info(f"プロンプトを実行しています: {command}")
                        result = subprocess.run(
                            command,
                            text=True,
                            capture_output=True,
                            check=True,
                            shell=True,
                        )
                        logging.info(f"gemini cli 実行結果 (stdout):\n{result.stdout}")
                        if result.stderr:
                            logging.warning(
                                f"gemini cli 実行結果 (stderr):\n{result.stderr}"
                            )

                    except subprocess.CalledProcessError as e:
                        if _handle_subprocess_error(e, run_once):
                            continue
                        break
                    except Exception as e:
                        logging.error(
                            f"タスク実行中に予期せぬエラーが発生しました: {e}"
                        )
                else:
                    logging.warning(
                        "割り当てられたタスクにプロンプトが含まれていません。"
                    )

                logging.info("タスクの実行プロセスが完了しました。")
                if run_once:
                    break
                time.sleep(SUCCESS_SLEEP_SECONDS)
            else:
                logging.info(
                    f"利用可能なタスクがありません。{NO_TASK_SLEEP_SECONDS // 60}分後に再試行します。"
                )
                if run_once:
                    break
                time.sleep(NO_TASK_SLEEP_SECONDS)

        except Exception as e:
            logging.error(
                f"エラーが発生しました: {e}。{ERROR_SLEEP_SECONDS // 60}分後に再試行します..."
            )
            if run_once:
                break
            time.sleep(ERROR_SLEEP_SECONDS)


if __name__ == "__main__":
    main()
