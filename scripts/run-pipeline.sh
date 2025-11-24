#!/bin/bash
# 生产环境定时调用脚本，可配合 cron 使用
set -e

cd "$(dirname "$0")/.."
source backend/venv/bin/activate

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

python backend/pipeline.py full
RESULT=$?

if [ $RESULT -eq 0 ]; then
  echo "[$(date)] Pipeline completed successfully"
  if [ -n "$WEBHOOK_URL" ]; then
    curl -X POST "$WEBHOOK_URL" -d "text=TrendForge: Daily generation complete"
  fi
else
  echo "[$(date)] Pipeline failed"
  if [ -n "$WEBHOOK_URL" ]; then
    curl -X POST "$WEBHOOK_URL" -d "text=⚠️ TrendForge: Pipeline failed"
  fi
fi
