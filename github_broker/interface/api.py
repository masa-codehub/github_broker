import logging

from fastapi import Depends, FastAPI, Request, Response, status, HTTPException
from fastapi.responses import JSONResponse

from github_broker.application.exceptions import LockAcquisitionError
from github_broker.application.task_service import TaskService
from github_broker.application.webhook_service import WebhookService # 追加
from github_broker.infrastructure.di_container import container
from github_broker.interface.models import AgentTaskRequest, TaskResponse

logger = logging.getLogger(__name__)


app = FastAPI()


def get_task_service() -> TaskService:
    return container.resolve(TaskService)

def get_webhook_service() -> WebhookService: # 追加
    return container.resolve(WebhookService)


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
        timeout=task_request.timeout,
    )
    if task:
        return task
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/api/v1/webhook/github", status_code=status.HTTP_202_ACCEPTED) # 追加
async def github_webhook_endpoint(
    request: Request,
    webhook_service: WebhookService = Depends(get_webhook_service),
):
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        logger.warning("X-Hub-Signature-256 header missing.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Hub-Signature-256 header missing")

    body = await request.body()

    try:
        webhook_service.process_webhook(signature, body)
    except ValueError as e:
        logger.warning(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    logger.info("Webhook payload received and enqueued.")
    return {"message": "Webhook received and enqueued."}
