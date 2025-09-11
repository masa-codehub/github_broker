import logging

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.config import Settings
from github_broker.infrastructure.di_container import get_container

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the GitHub Broker polling service...")

    container = get_container()
    settings = container.resolve(Settings)
    task_service = container.resolve(TaskService)

    logging.info(f"Target Repository: {settings.GITHUB_REPOSITORY}")
    logging.info("Starting task polling...")
    task_service.start_polling()
