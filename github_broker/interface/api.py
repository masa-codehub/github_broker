import logging

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from github_broker.application.exceptions import LockAcquisitionError
from github_broker.application.task_service import TaskService
from github_broker.infrastructure.di_container import get_container
from github_broker.interface.models import AgentTaskRequest, TaskResponse

logger = logging.getLogger(__name__)


def get_task_service() -> TaskService:
    return get_container().resolve(TaskService)


app = FastAPI()


@app.exception_handler(LockAcquisitionError)
async def lock_acquisition_exception_handler(
    request: Request, exc: LockAcquisitionError
):
    logger.error(f"Lock acquisition failed for request {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"message": str(exc)},
    )


@app.post(
    "/request-task",
    response_model=TaskResponse,
    responses={204: {"description": "No task available"}},
)
async def request_task_endpoint(
    task_request: AgentTaskRequest,
    task_service: TaskService = Depends(get_task_service),
):
    logger.info(f"Received task request from agent: {task_request.agent_id}")
    task = task_service.request_task(
        agent_id=task_request.agent_id,
        agent_role=task_request.agent_role,
    )
    if task:
        return task
    return Response(status_code=status.HTTP_204_NO_CONTENT)
