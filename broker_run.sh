#!/bin/sh

# GitHub CLIの認証設定
gh auth setup-git

# 外部モジュールのインストール
pip install -U -r .build/repositories.txt && pip install -e .

# ファイルの存在を確認（main.pyに変える）
if [ -f "broker_main.py" ]; then
    echo "main process start"
    python "broker_main.py"
fi
echo "main process done"
