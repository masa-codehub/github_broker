#!/bin/sh

# GitHub CLIの認証設定
gh auth setup-git

# GCP認証設定スクリプトの実行
bash ./.build/setup_gemini_auth.sh

# Gemini CLIのインストールと更新
npm update && npm install -g @google/gemini-cli

# 外部モジュールのインストール
pip install -U -r .build/repositories.txt && pip install -e .

# エージェント切り替え変更
bash .build/update_gemini_context.sh

# pre-commitの設定
pre-commit install --install-hooks

# ファイルの存在を確認（main.pyに変える）
if [ -f "sample_agent.py" ]; then
    echo "main process start"
    python "sample_agent.py"
fi
echo "main process done"
