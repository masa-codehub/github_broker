import os

import punq
from redis import Redis

from github_broker.application.task_service import TaskService
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient

# DIコンテナの初期化
container = punq.Container()

# RedisClientの登録
# 環境変数からRedisの接続情報を取得
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_db = int(os.getenv("REDIS_DB", 0))
# Redisインスタンスを作成
redis_instance = Redis(host=redis_host, port=redis_port, db=redis_db)
# RedisClientをシングルトンとしてコンテナに登録
container.register(RedisClient, instance=RedisClient(redis_instance))

# GitHubClientの登録
container.register(GitHubClient, scope=punq.Scope.singleton)

# TaskServiceの登録
container.register(
    TaskService,
    instance=TaskService(
        redis_client=container.resolve(RedisClient),
        github_client=container.resolve(GitHubClient),
    ),
    scope=punq.Scope.singleton,
)
