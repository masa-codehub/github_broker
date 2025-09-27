#!/bin/bash

# =============================================================================
# Gemini サービスアカウント認証スクリプト (Docker Secrets規約版 / 自動承認)
# =============================================================================
# 概要:
#   Docker Secretsでコンテナに渡されたサービスアカウントキーを使用して、
#   認証とプロジェクト設定を非対話的に行います。
#   gcloudコマンドには--quietオプションを付与し、全てのプロンプトを自動承認します。
# =============================================================================

set -e

# --- 設定規約 ---
# Docker SecretsでマウントされるGCPキーの固定パスを定義
readonly GCP_KEY_SECRET_PATH="/run/secrets/gcp_access_key"
# -----------------


# --- メイン処理 ---

echo "--- サービスアカウントによる認証設定を開始します ---"

# 環境変数 GOOGLE_CLOUD_PROJECT をチェック
if [ -z "${GOOGLE_CLOUD_PROJECT}" ]; then
  echo "エラー: 環境変数 GOOGLE_CLOUD_PROJECT が設定されていません。"
  echo "ヒント: .envファイルで設定してください。"
  exit 1
fi
echo "プロジェクトID: ${GOOGLE_CLOUD_PROJECT} を使用します。"

# 規約で定義した変数を使ってキーファイルの存在を確認
if [ ! -f "${GCP_KEY_SECRET_PATH}" ]; then
  echo "エラー: Docker Secretファイルが見つかりません。"
  echo "パスを確認してください: ${GCP_KEY_SECRET_PATH}"
  echo "ヒント: docker-compose.ymlのsecrets設定を確認してください。"
  exit 1
fi
echo "キーファイル: ${GCP_KEY_SECRET_PATH} を使用します。"
echo ""

# ステップ1: サービスアカウントの有効化
echo "ステップ1/2: サービスアカウントを有効化します..."
# --quietオプションを追加して、承認プロンプトを自動で承諾
gcloud auth activate-service-account --key-file="${GCP_KEY_SECRET_PATH}" --quiet
echo "✅ ステップ1 完了"
echo ""

# ステップ2: CLIの操作対象プロジェクトの設定
echo "ステップ2/2: 操作対象プロジェクトを設定します..."
# --quietオプションを追加して、承認プロンプトを自動で承諾
gcloud config set project "${GOOGLE_CLOUD_PROJECT}" --quiet
echo "✅ ステップ2 完了"
echo ""

echo "============================================================"
echo "🎉 すべての認証設定が正常に完了しました！"
echo "============================================================"
echo ""
echo "設定内容の確認:"
echo "・アクティブなアカウント: $(gcloud auth list --filter=status:ACTIVE --format='value(account)')"
echo "・アクティブなプロジェクト: $(gcloud config get-value project)"