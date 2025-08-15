import uvicorn
import os
from github_broker.interface.api import app

if __name__ == "__main__":
    # 環境変数 `APP_PORT` からポート番号を読み込む。指定がなければデフォルトで8080を使用。
    port = int(os.getenv("APP_PORT", 8080))
    github_token = os.getenv("GH_TOKEN", "NOT_SET")
    github_repo = os.getenv("GITHUB_REPOSITORY", "NOT_SET")
    print(f"GH_TOKEN: {github_token}")
    print(f"GITHUB_REPOSITORY: {github_repo}")
    uvicorn.run(app, host="0.0.0.0", port=port)
