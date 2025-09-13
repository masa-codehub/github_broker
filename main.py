import logging
import threading
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from github_broker.application.exceptions import LockAcquisitionError
from github_broker.application.task_service import TaskService
from github_broker.infrastructure.config import Settings
from github_broker.infrastructure.di_container import get_container
from github_broker.interface.api import router as api_router

logger = logging.getLogger(__name__)

stop_event = threading.Event()


def run_polling_service(stop_event: threading.Event):
    """バックグラウンドのポーリングサービスを初期化して実行します。"""
    logger.info("Starting the GitHub Broker polling service...")
    container = get_container()
    task_service = container.resolve(TaskService)
    logger.info(f"Target Repository: {task_service.repo_name}")
    task_service.start_polling(stop_event)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Uvicorn server starting up...")
    polling_thread = threading.Thread(
        target=run_polling_service, args=(stop_event,), name="PollingService"
    )
    polling_thread.start()
    try:
        yield
    finally:
        # Shutdown
        logger.info("Uvicorn server shutting down...")
        stop_event.set()
        polling_thread.join()
        logger.info("Polling service stopped.")


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.exception_handler(LockAcquisitionError)
async def lock_acquisition_exception_handler(
    request: Request, exc: LockAcquisitionError
):
    logger.error(f"Lock acquisition failed for request {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"message": str(exc)},
    )


def run_api_server():
    """Uvicorn APIサーバーを初期化して実行します。"""
    settings = Settings()
    logger.info(f"Starting Uvicorn server on 0.0.0.0:{settings.BROKER_PORT}...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.BROKER_PORT,
        reload=False,  # 本番環境ではFalseに設定
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_api_server()
