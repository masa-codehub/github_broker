#!/bin/sh

# GCP認証設定スクリプトの実行
bash ./.build/setup_gemini_auth.sh

# Gemini CLIのインストールと更新
npm update && npm install -g @google/gemini-cli

# 外部モジュールのインストール
pip install -U -r .build/repositories.txt && pip install -e .

# エージェント切り替え変更
bash .build/update_gemini_context.sh

# # ファイルの存在を確認
# if [ -f "main.py" ]; then
#     echo "main process start"
#     python "main.py"
# fi
# echo "main process done"
