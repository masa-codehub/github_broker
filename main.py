import uvicorn
import os
from github_broker.interface.api import app

if __name__ == "__main__":
    # 環境変数 `APP_PORT` からポート番号を読み込む。指定がなければデフォルトで8000を使用。
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
