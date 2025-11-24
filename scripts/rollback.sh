#!/bin/bash
# 紧急回滚脚本：回退到上一个提交并清理当日内容
set -e

echo "==================================="
echo "TrendForge Emergency Rollback"
echo "==================================="

LAST_GOOD=$(git log --format="%H" -n 2 | tail -1)
if [ -z "$LAST_GOOD" ]; then
  echo "未找到可回滚的提交" && exit 1
fi

echo "回滚到: $LAST_GOOD"
git branch backup-$(date +%Y%m%d-%H%M%S)
git reset --hard "$LAST_GOOD"

TODAY=$(date +%Y-%m-%d)
rm -f content/blog/*${TODAY}*.md || true

git add .
git commit -m "rollback: revert to $LAST_GOOD due to pipeline issues" || true
git push --force

echo "回滚完成，已创建备份分支"
