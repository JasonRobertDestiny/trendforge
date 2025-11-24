#!/bin/bash

# TrendForge 快速启动脚本
# 用于测试完整的内容生成流程

echo "======================================"
echo "TrendForge MVP 快速启动"
echo "======================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3未安装${NC}"
    exit 1
fi

# 检查Node
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ Node.js/npm未安装${NC}"
    exit 1
fi

echo -e "\n${GREEN}1. 运行后端Pipeline...${NC}"
echo "----------------------------------------"

# 运行测试pipeline
cd /mnt/d/gitlab_deepwisdom/trendforge
python3 backend/test_pipeline.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Pipeline执行成功${NC}"
else
    echo -e "${RED}✗ Pipeline执行失败${NC}"
    exit 1
fi

echo -e "\n${GREEN}2. 启动前端网站...${NC}"
echo "----------------------------------------"

# 检查是否已安装依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 启动前端
cd frontend
echo -e "${YELLOW}启动开发服务器...${NC}"
echo -e "${GREEN}网站地址: http://localhost:3000${NC}"
echo -e "${YELLOW}按 Ctrl+C 退出${NC}\n"

npm run dev

echo -e "\n${GREEN}======================================"
echo "TrendForge 已停止"
echo "======================================${NC}"