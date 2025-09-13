import logging
import multiprocessing

import uvicorn

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.config import Settings
from github_broker.infrastructure.di_container import get_container


def run_polling_service():
    """バックグラウンドのポーリングサービスを初期化して実行します。"""
    logging.info("Starting the GitHub Broker polling service...")
    container = get_container()
    task_service = container.resolve(TaskService)
    logging.info(f"Target Repository: {task_service.repo_name}")
    task_service.start_polling()


def run_api_server():
    """Uvicorn APIサーバーを初期化して実行します。"""
    settings = Settings()
    logging.info(f"Starting Uvicorn server on 0.0.0.0:{settings.BROKER_PORT}...")
    uvicorn.run(
        "github_broker.interface.api:app",
        host="0.0.0.0",
        port=settings.BROKER_PORT,
        reload=False,  # 本番環境ではFalseに設定
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 2つの別々のプロセスを作成します
    polling_process = multiprocessing.Process(
        target=run_polling_service, name="PollingService"
    )
    api_process = multiprocessing.Process(target=run_api_server, name="APIServer")

    # 両方のプロセスを開始します
    polling_process.start()
    api_process.start()

    try:
        # 両方のプロセスが完了するのを待ちます
        polling_process.join()
        api_process.join()
    except KeyboardInterrupt:
        logging.info("シャットダウン中...")
        polling_process.terminate()
        api_process.terminate()
        polling_process.join()
        api_process.join()
        logging.info("シャットダウン完了。")
