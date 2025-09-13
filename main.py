import logging
import multiprocessing

import uvicorn

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.config import Settings
from github_broker.infrastructure.di_container import get_container


def run_polling_service():
    """Initializes and runs the background polling service."""
    logging.info("Starting the GitHub Broker polling service...")
    container = get_container()
    task_service = container.resolve(TaskService)
    logging.info(f"Target Repository: {task_service.repo_name}")
    task_service.start_polling()


def run_api_server():
    """Initializes and runs the Uvicorn API server."""
    settings = Settings()
    logging.info(f"Starting Uvicorn server on 0.0.0.0:{settings.BROKER_PORT}...")
    uvicorn.run(
        "github_broker.interface.api:app",
        host="0.0.0.0",
        port=settings.BROKER_PORT,
        reload=False,  # Set to False for production
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create two separate processes
    polling_process = multiprocessing.Process(target=run_polling_service)
    api_process = multiprocessing.Process(target=run_api_server)

    # Start both processes
    polling_process.start()
    api_process.start()

    # Wait for both processes to complete (they won't, in this case, but it's good practice)
    polling_process.join()
    api_process.join()
