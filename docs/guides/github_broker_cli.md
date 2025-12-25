# GitHub Broker 運用CLIガイド

このドキュメントは、`github_broker` の運用および開発時に使用するCLIツールとコマンドについて説明します。

## 1. サーバーの起動

`github_broker` のAPIサーバーを起動するには、以下のコマンドを使用します。

```bash
# プロジェクトルートで実行
python3 broker_main.py
```

- **ポート:** デフォルトは `8000` (または `config.py` / 環境変数 `BROKER_PORT` で指定)
- **ホスト:** `0.0.0.0` (すべてのインターフェースでリッスン)

## 2. 運用管理スクリプト

`scripts/` ディレクトリには、開発やデバッグ、運用を補助するスクリプトが含まれています。

### Redis キャッシュ管理 (`redis_cli.sh`)

Redisの状態を操作するためのラッパースクリプトです。

**使用法:**

```bash
./scripts/redis_cli.sh <command> [arguments]
```

**コマンド一覧:**

| コマンド | 引数 | 説明 |
| :--- | :--- | :--- |
| `flush_all` | なし | Redisキャッシュを全て削除します (`FLUSHALL`)。 |
| `set_issue` | `<issue_number>` | 指定されたGitHub Issueの情報を取得し、Redisキャッシュに手動でセットします。デバッグ時に便利です。 |

**実行例:**

```bash
# キャッシュの全削除
./scripts/redis_cli.sh flush_all

# Issue #123 の情報をRedisにロード
./scripts/redis_cli.sh set_issue 123
```

## 3. ドキュメント検証

ドキュメントの整合性を検証するスクリプトも用意されています。

```bash
# 全ドキュメントの検証 (リンク切れチェックなど)
./scripts/validate_docs.sh
```
