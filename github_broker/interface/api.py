import logging

from fastapi import APIRouter, Depends, Response, status

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.di_container import get_container
from github_broker.interface.models import AgentTaskRequest, TaskResponse

logger = logging.getLogger(__name__)


def get_task_service() -> TaskService:
    return get_container().resolve(TaskService)


router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}


@router.post(
    "/request-task",
    response_model=TaskResponse,
    responses={204: {"description": "No task available"}},
)
async def request_task_endpoint(
    task_request: AgentTaskRequest,
    task_service: TaskService = Depends(get_task_service),
):
    logger.info(f"Received task request from agent: {task_request.agent_id}")
    task = await task_service.request_task(
        agent_id=task_request.agent_id,
        agent_role=task_request.agent_role,
        timeout=task_request.timeout,
    )
    if task:
        return task
    return Response(status_code=status.HTTP_204_NO_CONTENT)
