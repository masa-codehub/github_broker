import logging

import uvicorn

from github_broker.infrastructure.config import Settings
from github_broker.infrastructure.di_container import get_container
from github_broker.interface.api import app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    settings = get_container().resolve(Settings)
    logging.info(f"GITHUB_REPOSITORY: {settings.GITHUB_REPOSITORY}")
    uvicorn.run(app, host="0.0.0.0", port=settings.BROKER_PORT)
