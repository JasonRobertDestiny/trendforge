#!/bin/bash
# 本地 CI 快速自测脚本
set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "==================================="
echo "TrendForge Local CI Test"
echo "==================================="

echo -e "${YELLOW}检查环境...${NC}"

command -v python3 >/dev/null && echo -e "${GREEN}✓ Python $(python3 --version)${NC}" || { echo -e "${RED}✗ 缺少 Python${NC}"; exit 1; }
command -v node >/dev/null && echo -e "${GREEN}✓ Node $(node --version)${NC}" || { echo -e "${RED}✗ 缺少 Node${NC}"; exit 1; }
command -v git >/dev/null && echo -e "${GREEN}✓ Git $(git --version)${NC}" || { echo -e "${RED}✗ 缺少 Git${NC}"; exit 1; }

echo ""
echo -e "${YELLOW}运行后端管线...${NC}"
cd "$(dirname "$0")/.."

if [ ! -d "backend/venv" ]; then
  python3 -m venv backend/venv
fi
source backend/venv/bin/activate
pip install -q -r backend/requirements.txt

if [ ! -f "backend/config/api_config.yaml" ]; then
  echo -e "${RED}✗ 未找到 backend/config/api_config.yaml${NC}"
  echo "请从模板复制并填写必要密钥"
  exit 1
fi

python backend/pipeline.py test || true

if ls content/blog/*.md 1>/dev/null 2>&1; then
  COUNT=$(ls -1 content/blog/*.md | wc -l)
  echo -e "${GREEN}✓ 文章存在: ${COUNT} 篇${NC}"
else
  echo -e "${YELLOW}⚠ 未找到文章，可能需要先运行 full${NC}"
fi

echo ""
echo -e "${YELLOW}测试前端构建...${NC}"
cd frontend
npm install >/dev/null
npm run build >/dev/null
[ -d "out" ] && echo -e "${GREEN}✓ 前端构建成功${NC}" || { echo -e "${RED}✗ 前端构建失败${NC}"; exit 1; }

echo ""
echo "==================================="
echo -e "${GREEN}本地 CI 自测完成${NC}"
echo "==================================="
