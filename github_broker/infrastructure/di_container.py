import punq
from redis import Redis

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.config import Settings
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient

_container: punq.Container | None = None


def _create_container() -> punq.Container:
    """
    DIコンテナを初期化し、依存関係を手動で構築して登録します。
    punqの自動解決機能は使用せず、明示的な依存性注入を行います。
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

    # 3. 構築した依存関係をすべて使ってTaskServiceをインスタンス化
    task_service = TaskService(
        redis_client=redis_client,
        github_client=github_client,
        settings=settings,
    )

    # 4. すべての主要なインスタンスをコンテナに登録
    container.register(Settings, instance=settings)
    container.register(RedisClient, instance=redis_client)
    container.register(GitHubClient, instance=github_client)
    container.register(TaskService, instance=task_service)

    return container


def get_container() -> punq.Container:
    """
    シングルトンDIコンテナを返します。

    コンテナがまだ初期化されていない場合は、この関数が最初の呼び出しで
    コンテナを生成します。これにより、テスト中に環境変数を設定した後に
    コンテナを初期化するなどの柔軟な対応が可能になります。
    """
    global _container
    if _container is None:
        _container = _create_container()
    return _container
