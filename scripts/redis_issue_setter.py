import json
import os
import sys

import redis

from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient


def get_github_issue(github_client: GitHubClient, issue_number: int):
    """
    GitHubから特定のIssueを取得します。
    """
    try:
        return github_client.get_issue_by_number(issue_number)
    except Exception as e:
        print(f"Error fetching issue {issue_number} from GitHub: {e}")  # noqa: T201
        sys.exit(1)


def set_issue_in_redis(redis_client: RedisClient, issue_number: int, issue_data: dict):
    """
    IssueデータをRedisに保存します。
    """
    key = f"github_issue:{issue_number}"
    try:
        redis_client.set_value(key, json.dumps(issue_data))
        print(f"Issue {issue_number} data set in Redis with key: {key}")  # noqa: T201
    except Exception as e:
        print(f"Error setting issue {issue_number} in Redis: {e}")  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 redis_issue_setter.py <issue_number>")  # noqa: T201
        sys.exit(1)

    try:
        issue_number = int(sys.argv[1])
    except ValueError:
        print("Error: <issue_number> must be a valid integer.")  # noqa: T201
        sys.exit(1)

    # 環境変数からGitHubトークンとリポジトリ名を取得
    github_token = os.getenv("GITHUB_TOKEN")
    github_repository = os.getenv("GITHUB_REPOSITORY")

    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set.")  # noqa: T201
        sys.exit(1)
    if not github_repository:
        print("Error: GITHUB_REPOSITORY environment variable not set.")  # noqa: T201
        sys.exit(1)

    # GitHubクライアントの初期化
    github_client = GitHubClient(
        github_repository=github_repository, github_token=github_token
    )

    # Redisクライアントの初期化
    # TODO: Redis接続設定をSettingsクラスから取得するようにリファクタリングする
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_db = int(os.getenv("REDIS_DB", 0))

    try:
        owner, repo_name = github_repository.split("/")
    except ValueError:
        print("Error: GITHUB_REPOSITORY must be in 'owner/repo_name' format.")  # noqa: T201
        sys.exit(1)

    try:
        r = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db, decode_responses=True
        )
        redis_client = RedisClient(redis=r, owner=owner, repo_name=repo_name)
    except Exception as e:
        print(f"Error connecting to Redis: {e}")  # noqa: T201
        sys.exit(1)

    # Issueを取得してRedisに保存
    issue_data = get_github_issue(github_client, issue_number)
    set_issue_in_redis(redis_client, issue_number, issue_data)
