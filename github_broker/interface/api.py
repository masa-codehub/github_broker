import logging

from fastapi import APIRouter, Depends, Response, status

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.di_container import create_container
from github_broker.interface.models import AgentTaskRequest, TaskResponse

logger = logging.getLogger(__name__)


def get_task_service() -> TaskService:
    container = create_container()
    return container.resolve(TaskService)


router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}


@router.post(
    "/request-task",
    response_model=TaskResponse,
    responses={204: {"description": "No task available"}},
)
def request_task_endpoint(
    task_request: AgentTaskRequest,
    task_service: TaskService = Depends(get_task_service),
):
    """
    NOTE: This endpoint is temporarily stubbed out due to ongoing refactoring.
    """
    logger.info(f"Received task request from agent: {task_request.agent_id}")
    # The original logic is disabled as `request_task` signature has changed.
    # A new implementation is required based on the current TaskService.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/tasks/fix", status_code=status.HTTP_202_ACCEPTED)
def create_fix_task_endpoint(
    # request: CreateFixTaskRequest, # Model is not fully defined
    # background_tasks: BackgroundTasks,
    task_service: TaskService = Depends(get_task_service),
):
    """
    NOTE: This endpoint is temporarily stubbed out as `create_fix_task`
    method does not exist in TaskService anymore.
    """
    logger.info("Received fix task request.")
    return {"message": "Fix task creation has been accepted (stubbed)."}
