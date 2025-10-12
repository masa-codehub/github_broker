import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Response, status

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.di_container import get_container
from github_broker.interface.models import (
    AgentTaskRequest,
    CreateFixTaskRequest,
    TaskResponse,
)

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
        timeout=task_request.timeout,
    )
    if task:
        return task
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/tasks/fix", status_code=status.HTTP_202_ACCEPTED)
async def create_fix_task_endpoint(
    request: CreateFixTaskRequest,
    background_tasks: BackgroundTasks,
    task_service: TaskService = Depends(get_task_service),
):
    """レビューコメントに基づいて修正タスクの作成を受け付けます。"""
    logger.info(f"Received fix task request for PR #{request.pull_request_number}")
    # タスク作成をバックグラウンドで実行
    background_tasks.add_task(
        task_service.create_fix_task,
        pull_request_number=request.pull_request_number,
        review_comments=request.review_comments,
    )
    return {"message": "Fix task creation has been accepted."}
