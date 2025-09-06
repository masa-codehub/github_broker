import logging
import os
import threading

import uvicorn

# `di_container`モジュールをインポートして、コンテナが初期化されるようにします。
from github_broker.infrastructure import di_container
from github_broker.interface.api import app
from github_broker.application.issue_cache_updater_service import IssueCacheUpdaterService

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # RedisClientのインスタンスを取得
    redis_client = di_container.redis_client()

    # IssueCacheUpdaterServiceを初期化し、別スレッドで実行
    issue_updater_service = IssueCacheUpdaterService(redis_client)
    updater_thread = threading.Thread(target=issue_updater_service.start)
    updater_thread.daemon = True  # メインスレッド終了時に一緒に終了
    updater_thread.start()

    # 環境変数 `BROKER_PORT` からポート番号を読み込む。指定がなければデフォルトで8080を使用。
    port = int(os.getenv("BROKER_PORT", 8080))
    github_token = os.getenv("GITHUB_TOKEN", "NOT_SET")
    github_repo = os.getenv("GITHUB_REPOSITORY", "NOT_SET")
    # print(f"GITHUB_TOKEN: {github_token}")
    print(f"GITHUB_REPOSITORY: {github_repo}")
    uvicorn.run(app, host="0.0.0.0", port=port)
