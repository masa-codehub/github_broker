import logging

# TaskServiceは、GitHubリポジトリを定期的にポーリングしてIssueをキャッシュする主要なサービスです。
from github_broker.application.task_service import TaskService
from github_broker.infrastructure.di_container import get_container

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the GitHub Broker polling service...")

    container = get_container()
    task_service = container.resolve(TaskService)

    logging.info(f"Target Repository: {task_service.repo_name}")
    logging.info("Starting task polling...")
    # start_polling() はブロッキング呼び出しで、ポーリングサービスを開始します。
    # サービスは中断されるまで（例: Ctrl+C）、実行され続けます。
    task_service.start_polling()
