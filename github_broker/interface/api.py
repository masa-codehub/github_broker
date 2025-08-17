"""
FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from github_broker.application.exceptions import LockAcquisitionError
from github_broker.application.task_service import TaskService
from github_broker.infrastructure.di_container import (build_di_container,
                                                     shutdown_di_container)
from github_broker.interface.models import TaskRequest, TaskResponse

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle application startup and shutdown.
    """
    logger.info("Application startup: Initializing DI container.")
    await build_di_container()
    yield
    logger.info("Application shutdown: Tearing down DI container.")
    await shutdown_di_container()

app = FastAPI(lifespan=lifespan)

@app.exception_handler(LockAcquisitionError)
async def lock_acquisition_exception_handler(request: Request, exc: LockAcquisitionError):
    """
    Handles LockAcquisitionError by returning a 503 Service Unavailable response.
    """
    logger.error(f"Lock acquisition failed for request {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"message": str(exc)},
    )

@app.post("/request-task", response_model=TaskResponse)
async def request_task_endpoint(task_request: TaskRequest):
    """
    Endpoint to request a new task.
    """
    logger.info(f"Received task request for repository: {task_request.repo_url}")
    task_service = app.state.container.resolve(TaskService)
    task_id = task_service.request_task()
    return TaskResponse(task_id=task_id)