#!/bin/bash
set -e

echo "==================================="
echo "TrendForge Backend Setup"
echo "==================================="

# 创建虚拟环境
if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
fi
source venv/bin/activate

# 安装依赖
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# 安装 MetaGPT
echo "Installing MetaGPT DR module..."
pip install git+ssh://git@gitlab.deepwisdomai.com/pub/MetaGPT.git@dr4run || true

# 配置模板
if [ ! -f backend/config/api_config.yaml ]; then
  cp backend/config/api_config.yaml.template backend/config/api_config.yaml
  echo "⚠️  请在 backend/config/api_config.yaml 填写 API 密钥"
fi

# 创建目录
mkdir -p data/trending data/processed content/blog logs

echo "==================================="
echo "Setup complete!"
echo "Run: source venv/bin/activate && python backend/pipeline.py full"
echo "==================================="
