# ローカル環境でのシークレット管理

このドキュメントでは、開発環境で `GITHUB_TOKEN` および `GEMINI_API_KEY` を安全に管理し、`docker-compose` で利用するための手順を説明します。

## 必須: GITHUB_TOKEN の設定

`GITHUB_TOKEN` は、GitHub API との連携に必須のトークンです。これを Docker Secrets として安全に管理します。

1.  **`github_token.txt` ファイルの作成:**
    プロジェクトのルートディレクトリに `github_token.txt` という名前のファイルを作成し、その中にあなたの GitHub Personal Access Token (PAT) を記述します。

    ```bash
    echo "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN" > github_token.txt
    ```

    **重要:** このファイルは `.gitignore` に追加され、Git リポジトリにコミットされないようにしてください。

2.  **`docker-compose.yml` での利用:**
    `docker-compose.yml` は、この `github_token.txt` を Docker Secret として自動的に読み込み、`agent` および `github_broker` サービスに安全に渡します。

## オプション: GEMINI_API_KEY の設定

`GEMINI_API_KEY` は、Gemini API を利用する場合にのみ必要です。すべての開発者が利用するわけではないため、`docker-compose.override.yml` を使用してオプションで設定します。

1.  **`docker-compose.override.yml` ファイルの作成:**
    プロジェクトのルートディレクトリに `docker-compose.override.yml` という名前のファイルを作成します。このファイルは `docker-compose.yml` の設定を上書き・拡張するために使用されます。

    ```yaml
    # docker-compose.override.yml
    version: '3.8'

    services:
      agent:
        environment:
          - GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    ```

    `YOUR_GEMINI_API_KEY` の部分をあなたの Gemini API キーに置き換えてください。

    **重要:** このファイルも `.gitignore` に追加され、Git リポジトリにコミットされないようにしてください。

2.  **`docker-compose.override.yml` の利用:**
    `docker-compose` コマンドを実行する際、`docker-compose.override.yml` が存在すれば自動的に読み込まれます。これにより、`agent` サービスに `GEMINI_API_KEY` が環境変数として渡されます。

    ```bash
    docker-compose up -d
    ```

### まとめ

-   `GITHUB_TOKEN`: `github_token.txt` ファイルを作成し、その中にトークンを記述します。これは必須です。
-   `GEMINI_API_KEY`: `docker-compose.override.yml` を作成し、`agent` サービスの `environment` セクションで設定します。これはオプションです。

これらのファイルを Git にコミットしないように注意し、ローカル環境でのみ使用してください。
