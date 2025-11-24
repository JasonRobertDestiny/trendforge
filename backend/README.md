# TrendForge Backend

Python 管道：趋势抓取（HN/Reddit/GitHub，可选 MCP 聚合）→ 自动筛选/去重 → MetaGPT Deep Research 生成 Markdown → Git 提交触发前端发布。

## 运行前准备
1. 复制配置：`cp backend/config/api_config.yaml.template backend/config/api_config.yaml` 并按需填入 `newsapi_key`（缺省会跳过 NewsAPI）。
2. 安装依赖：
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```
3. 配置 MetaGPT：确保 `~/.metagpt/config2.yaml` 可用。

## 主要命令
- 抓取测试：`python backend/pipeline.py crawl`
- 全流程：`python backend/pipeline.py full`
- 启用 MCP Trends Hub：`python backend/pipeline.py full --use-mcp --mcp-base http://localhost:3000`

## 目录
- `crawlers/` 各数据源爬虫
- `utils/` 去重、筛选、存储
- `generators/` DR 集成
- `pipeline.py` 主入口
