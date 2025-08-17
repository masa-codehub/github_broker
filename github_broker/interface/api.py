import os
from fastapi import FastAPI, HTTPException, Response
from starlette.status import HTTP_204_NO_CONTENT, HTTP_503_SERVICE_UNAVAILABLE

from .models import TaskRequest, TaskResponse
from ..application.task_service import TaskService
from ..infrastructure.github_client import GitHubClient
from ..infrastructure.redis_client import RedisClient
from ..infrastructure.executors.gemini_executor import GeminiExecutor

# --- Dependency Injection Setup ---
# Create instances of our clients and service.
# In a real-world scenario, you might use a more sophisticated DI framework.
github_client = GitHubClient()

# Setup Redis client from environment variables
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = RedisClient(host=redis_host, port=redis_port)

# Get log_dir from environment variable for the executor
gemini_log_dir = os.getenv("GEMINI_LOG_DIR")
gemini_executor = GeminiExecutor(log_dir=gemini_log_dir)



# Get repository name from environment variable
repo_name = os.getenv("GITHUB_REPOSITORY")
if not repo_name:
    raise ValueError("GITHUB_REPOSITORY environment variable not set.")

task_service = TaskService(github_client=github_client, redis_client=redis_client,
                           gemini_executor=gemini_executor, repo_name=repo_name)
# --- --- --- --- --- --- --- --- ---

app = FastAPI(
    title="GitHub Task Broker",
    description="Assigns GitHub issues to worker agents intelligently and exclusively.",
    version="0.1.0",
)


@app.post("/api/v1/request-task", response_model=TaskResponse)
async def request_task(req: TaskRequest):
    """
    Handles a request from a worker agent for a new task.
    """
    try:
        new_task = task_service.request_task(
            agent_id=req.agent_id, capabilities=req.capabilities)

        if new_task:
            return new_task
        else:
            # No suitable task was found
            return Response(status_code=HTTP_204_NO_CONTENT)

    except Exception as e:
        # Specific exception handling could be better, but for now, this catches the "Server Busy" case.
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
