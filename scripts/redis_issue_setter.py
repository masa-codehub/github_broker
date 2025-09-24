import os
import sys
import json
import redis
from github_broker.infrastructure.github_client import GitHubClient
from github_broker.infrastructure.redis_client import RedisClient

def get_github_issue(github_client: GitHubClient, issue_number: int):
    """
    GitHubから特定のIssueを取得します。
    """
    try:
        repo = github_client._client.get_repo(github_client._repo_name)
        issue = repo.get_issue(number=issue_number)
        return issue.raw_data
    except Exception as e:
        print(f"Error fetching issue {issue_number} from GitHub: {e}")
        sys.exit(1)

def set_issue_in_redis(redis_client: RedisClient, issue_number: int, issue_data: dict):
    """
    IssueデータをRedisに保存します。
    """
    key = f"github_issue:{issue_number}"
    try:
        redis_client.set_value(key, json.dumps(issue_data))
        print(f"Issue {issue_number} data set in Redis with key: {key}")
    except Exception as e:
        print(f"Error setting issue {issue_number} in Redis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 redis_issue_setter.py <issue_number>")
        sys.exit(1)

    issue_number = int(sys.argv[1])

    # 環境変数からGitHubトークンとリポジトリ名を取得
    github_token = os.getenv("GITHUB_TOKEN")
    github_repository = os.getenv("GITHUB_REPOSITORY", "masa-codehub/github_broker") # デフォルト値を設定

    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    # GitHubクライアントの初期化
    github_client = GitHubClient(github_repository=github_repository, github_token=github_token)

    # Redisクライアントの初期化
    # TODO: Redis接続設定を環境変数から取得するようにする
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_db = int(os.getenv("REDIS_DB", 0))
    
    try:
        r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        redis_client = RedisClient(redis=r)
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        sys.exit(1)

    # Issueを取得してRedisに保存
    issue_data = get_github_issue(github_client, issue_number)
    set_issue_in_redis(redis_client, issue_number, issue_data)
