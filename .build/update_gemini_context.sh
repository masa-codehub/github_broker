#!/bin/bash

AGENT_ROLL_UPPER=$(echo $AGENT_ROLL | tr '[:lower:]' '[:upper:]')

if [ -z "$AGENT_ROLL_UPPER" ]; then
    echo "エラー: AGENT_ROLL 環境変数が設定されていません。" >&2
    exit 1
fi

GEMINI_MD_PATH="/app/.gemini/GEMINI.md"
AGENT_MD_PATH="/app/.gemini/AGENTS/${AGENT_ROLL_UPPER}.md"

if [ ! -f "$AGENT_MD_PATH" ]; then
    echo "エラー: エージェントロールファイルが $AGENT_MD_PATH に見つかりません。" >&2
    exit 1
fi

cp "$AGENT_MD_PATH" "$GEMINI_MD_PATH"

if [ $? -eq 0 ]; then
    echo "$GEMINI_MD_PATH を $AGENT_MD_PATH の内容で正常に更新しました。"
else
    echo "エラー: $AGENT_MD_PATH から $GEMINI_MD_PATH へのファイルコピーに失敗しました。" >&2
    exit 1
fi

# 環境変数 GITHUB_REPOSITORY が設定されている場合、GEMINI.md 内のリポジトリURLを書き換える
if [ -n "$GITHUB_REPOSITORY" ]; then
    NEW_REPO_URL="https://github.com/${GITHUB_REPOSITORY}.git"

    # GEMINI.md 内の既存のGitHubリポジトリURLを動的に検索
    # https://github.com/ で始まり、空白文字以外の文字が続くパターンを抽出
    OLD_REPO_URL=$(grep -oP 'https://github.com/[^[:space:]]+' "$GEMINI_MD_PATH" | head -n 1)

    if [ -z "$OLD_REPO_URL" ]; then
        echo "警告: $GEMINI_MD_PATH 内に既存のGitHubリポジトリURLが見つかりませんでした。置換はスキップされます。" >&2
    else
        # sed を使用してインプレースで置換
        # URLにスラッシュが含まれるため、区切り文字として | を使用
        sed -i "s|${OLD_REPO_URL}|${NEW_REPO_URL}|g" "$GEMINI_MD_PATH"
        if [ $? -eq 0 ]; then
            echo "$GEMINI_MD_PATH 内の GitHub リポジトリURLを $NEW_REPO_URL に更新しました。"
        else
            echo "エラー: $GEMINI_MD_PATH 内の GitHub リポジトリURLの更新に失敗しました。" >&2
            exit 1
        fi
    fi
fi

