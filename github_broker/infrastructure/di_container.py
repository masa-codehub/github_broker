import punq
from redis import Redis

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.config import Settings
from github_broker.infrastructure.gemini_client import GeminiClient
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient


def create_container() -> punq.Container:
    """
    DIコンテナを初期化し、TaskServiceに必要な依存関係を手動で構築して登録します。
    punqの自動解決機能は使用しません。
    """
    container = punq.Container()

    # 1. 依存関係のトップレベルであるSettingsをインスタンス化
    settings = Settings()  # type: ignore

    # 2. Settingsを使って、下位の依存関係を構築
    redis_instance = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )
    redis_client = RedisClient(redis=redis_instance)

    github_client = GitHubClient(
        github_repository=settings.GITHUB_REPOSITORY,
        github_token=settings.GITHUB_TOKEN,
    )

    gemini_client = GeminiClient(gemini_api_key=settings.GEMINI_API_KEY)

    # 3. 構築した依存関係をすべて使ってTaskServiceをインスタンス化
    task_service = TaskService(
        redis_client=redis_client,
        github_client=github_client,
        gemini_client=gemini_client,
        settings=settings,
    )

    # 4. 最終的に必要となるTaskServiceのインスタンスのみをコンテナに登録
    container.register(TaskService, instance=task_service)

    return container
