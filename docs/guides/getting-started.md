# Getting Started Guide for New Contributors

このガイドは、新規貢献者が `github_broker` プロジェクトの開発環境をセットアップし、基本的なタスク処理フローを理解するための手順を提供します。

## 1. はじめに

`github_broker` は、GitHub Issue を通じてタスクを管理し、AI エージェントが自動的にタスクを処理するシステムです。このガイドでは、ローカル環境でこのシステムを動かすための準備と、主要なコンポーネントの実行方法を説明します。

## 2. 必要なツール

開発を始める前に、以下のツールがインストールされ、最小バージョン要件を満たしていることを確認してください。

### Python

- **用途**: プロジェクトの主要な開発言語です。
- **最小バージョン**: 3.9 以上
- **インストール方法**: 公式サイト ([https://www.python.org/downloads/](https://www.python.org/downloads/)) からダウンロードしてインストールするか、`pyenv` などのバージョン管理ツールを使用してください。
- **バージョン確認**:
  ```bash
  python --version
  ```

### Docker & Docker Compose

- **用途**: Redis などのコンテナ化されたサービスを実行するために必要です。
- **最小バージョン**: Docker Engine 20.10.0 以上, Docker Compose v2.0.0 以上
- **インストール方法**:
    - **Windows/macOS**: [Docker Desktop](https://www.docker.com/products/docker-desktop) をインストールしてください。
    - **Linux**: 公式ドキュメント ([https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)) を参照してください。
- **バージョン確認**:
  ```bash
  docker --version
  docker compose version
  ```

### Git

- **用途**: ソースコードのバージョン管理に使用します。
- **インストール方法**: 各OSのパッケージマネージャーを使用するか、公式ドキュメントを参照してください。
- **バージョン確認**:
  ```bash
  git --version
  ```

## 3. リポジトリのクローン

まず、プロジェクトのリポジトリをローカルにクローンします。

```bash
git clone https://github.com/masa-codehub/github_broker.git
cd github_broker
```

## 4. Python 依存関係のインストール

プロジェクトの Python 依存関係をインストールし、開発モードでパッケージをセットアップします。

```bash
pip install -e .
```

## 5. シークレット管理 (`.env` ファイルのセットアップ)

`github_broker` は GitHub API と Gemini API を利用するため、API キーのセットアップが必要です。これらのシークレットは、`.env` ファイルまたは Docker Secrets を使用して管理します。

### 5.1. `GITHUB_TOKEN` の設定 (必須)

GitHub API との連携に必須のトークンです。

1.  **GitHub Personal Access Token (PAT) の取得**:
    -   GitHub の設定ページで、`repo` スコープを持つ PAT を生成してください。
    -   詳細な手順は [GitHub Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) を参照してください。
2.  **`.env` ファイルの作成**:
    プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の内容を記述します。

    ```ini
    # .env
    GITHUB_TOKEN=YOUR_GITHUB_PERSONAL_ACCESS_TOKEN
    ```
    `YOUR_GITHUB_PERSONAL_ACCESS_TOKEN` の部分を、取得した PAT に置き換えてください。

### 5.2. `GEMINI_API_KEY` の設定 (オプション)

Gemini API を利用する場合にのみ必要です。

1.  **Gemini API キーの取得**:
    -   Google AI Studio ([https://aistudio.google.com/](https://aistudio.google.com/)) で API キーを生成してください。
2.  **`.env` ファイルへの追加**:
    `.env` ファイルに以下の行を追加します。

    ```ini
    # .env
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    ```
    `YOUR_GEMINI_API_KEY` の部分を、取得した Gemini API キーに置き換えてください。

**重要**: `.env` ファイルは `.gitignore` に追加されており、Git リポジトリにコミットされないように設定されています。機密情報が誤って公開されないよう、この設定を変更しないでください。

## 6. 開発環境の起動とタスク処理の確認

### 6.1. Docker コンテナの起動

Redis などの依存サービスを Docker で起動します。

```bash
docker compose -f .build/context/docker-compose.yml up -d
```

### 6.2. `broker_main.py` の実行

`broker_main.py` は、GitHub Issue を監視し、エージェントにタスクを割り当てる役割を担います。

```bash
python broker_main.py
```

このコマンドを実行すると、ブローカーが起動し、GitHub リポジトリの Issue をポーリングし始めます。

### 6.3. `agents_main.py` の実行

`agents_main.py` は、ブローカーから割り当てられたタスクを処理する AI エージェントを起動します。

```bash
python agents_main.py
```

このコマンドを実行すると、エージェントが起動し、ブローカーにタスクを要求し、割り当てられたタスクを処理しようとします。

### 6.4. タスク処理フローの確認

1.  GitHub リポジトリで新しい Issue を作成します。例えば、`test` というラベルを付けた Issue を作成します。
2.  `broker_main.py` がその Issue を検出し、`agents_main.py` にタスクとして割り当てます。
3.  `agents_main.py` がタスクを受け取り、処理を開始します。処理が完了すると、Issue の状態が更新されるはずです。
4.  `docker compose logs -f` コマンドで、すべてのサービスのログをリアルタイムで確認できます。

    ```bash
    docker compose -f .build/context/docker-compose.yml logs -f
    ```

## 7. トラブルシューティング

### Q. `GITHUB_TOKEN` または `GEMINI_API_KEY` が認識されない。

-   `.env` ファイルがプロジェクトのルートディレクトリに正しく配置されているか確認してください。
-   環境変数の名前 (`GITHUB_TOKEN`, `GEMINI_API_KEY`) が正しいか確認してください。
-   `broker_main.py` や `agents_main.py` を実行する前に、ターミナルを再起動して環境変数がロードされていることを確認してください。

### Q. Docker コンテナが起動しない、またはエラーが発生する。

-   Docker Desktop が起動しているか確認してください。
-   `docker compose -f .build/context/docker-compose.yml logs` でエラーログを確認し、原因を特定してください。
-   ポートの競合がないか確認してください（例: Redis のデフォルトポート 6379 が他のアプリケーションで使用されていないか）。

### Q. `pip install -e .` でエラーが発生する。

-   Python のバージョンが 3.9 以上であることを確認してください。
-   `pip` が最新バージョンであることを確認してください (`python -m pip install --upgrade pip`)。
-   エラーメッセージをよく読み、不足しているシステム依存関係がないか確認してください。

## 8. 次のステップ

基本的な開発環境のセットアップとタスク処理フローの確認が完了しました。
次に、以下のドキュメントを参照して、プロジェクトへの貢献を深めてください。

-   [開発ワークフロー](./development-workflow.md): プロジェクトの全体的な開発プロセスと、各フェーズでのエージェントの役割について。
-   [階層的要件管理ワークフロー](./requirement-management-workflow.md): Issue の階層構造と管理方法について。
-   [コーディングガイドライン](../guides/coding-guidelines.md): コードの品質と一貫性を保つための規約。
