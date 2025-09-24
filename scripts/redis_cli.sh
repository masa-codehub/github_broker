#!/bin/bash

COMMAND=$1
ISSUE_NUMBER=$2

case "$COMMAND" in
    flush_all)
        echo "Flushing all Redis cache..."
        redis-cli flushall
        echo "Redis cache flushed."
        ;;
    set_issue)
        if [ -z "$ISSUE_NUMBER" ]; then
            echo "Usage: ./scripts/redis_cli.sh set_issue <issue_number>"
            exit 1
        fi
        echo "Setting issue $ISSUE_NUMBER in Redis cache..."
        python3 /app/scripts/redis_issue_setter.py "$ISSUE_NUMBER"
        echo "Issue $ISSUE_NUMBER set in Redis cache."
        ;;
    *)
        echo "Usage: ./scripts/redis_cli.sh <command> [arguments]"
        echo "Commands:"
        echo "  flush_all                       - Flushes all Redis cache."
        echo "  set_issue <issue_number>        - Fetches a GitHub issue and sets it in Redis cache."
        exit 1
        ;;
esac
