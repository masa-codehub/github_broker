import logging
import threading

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

    # ポーリングサービスをバックグラウンドスレッドで開始します
    polling_thread = threading.Thread(
        target=run_polling_service, name="PollingService", daemon=True
    )
    polling_thread.start()

    # メインスレッドでAPIサーバーを実行します
    run_api_server()
