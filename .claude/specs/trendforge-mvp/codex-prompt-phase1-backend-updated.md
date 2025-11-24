# TrendForge Backend Pipeline - Development Prompt for Codex (Updated)

## Project Context

You are building the backend pipeline for TrendForge, an automated content generation system using MetaGPT's Deep Research (DR) capability. The DR module generates comprehensive research articles that serve directly as blog content.

**Repository**: Empty GitLab repository at `/mnt/d/gitlab_deepwisdom/trendforge/`

## Core Workflow

```
Trending抓取 → 自动筛选 → DR生成深度文章 → Git保存 → 自动推送到网站
```

**Key Point**: DR生成的深度研究报告就是最终的blog内容，无需额外转换。

## Your Task

Build the Python backend pipeline that:
1. Fetches trending topics from multiple sources (HackerNews, Reddit, News API)
2. Automatically filters based on engagement and relevance rules
3. Uses MetaGPT DR to generate comprehensive research articles
4. Saves articles as Markdown files
5. Commits to Git (triggers website deployment)

## Technical Requirements

### 1. Project Structure

```
trendforge/
├── backend/
│   ├── config/
│   │   ├── api_config.yaml      # API keys (template)
│   │   ├── filter_rules.yaml    # Auto-filter configuration
│   │   └── dr_config.yaml       # DR generation settings
│   ├── crawlers/
│   │   ├── __init__.py
│   │   ├── base_crawler.py      # Abstract base class
│   │   ├── hackernews.py        # HackerNews crawler
│   │   ├── reddit.py            # Reddit crawler
│   │   └── newsapi.py           # News API crawler
│   ├── generators/
│   │   ├── __init__.py
│   │   └── dr_generator.py      # MetaGPT DR integration
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── deduplicator.py      # Remove duplicate topics
│   │   ├── filter.py            # Auto-filter logic
│   │   └── storage.py           # Git operations
│   ├── pipeline.py              # Main orchestrator
│   ├── requirements.txt
│   └── README.md
├── data/
│   ├── trending/                # Daily trending data
│   └── processed/               # Filtered trending
└── content/
    └── blog/                     # DR-generated articles
```

### 2. Dependencies (requirements.txt)

```txt
requests==2.31.0
beautifulsoup4==4.12.2
pyyaml==6.0.1
gitpython==3.1.40
schedule==1.2.0
python-dotenv==1.0.0
aiohttp==3.9.1
asyncio==3.4.3
metagpt  # Install via: pip install git+ssh://git@gitlab.deepwisdomai.com/pub/MetaGPT.git@dr4run
```

### 3. MetaGPT DR Integration (generators/dr_generator.py)

```python
from metagpt.environment.mgx.mgx_env import MGXEnv
from metagpt.roles.dr.research_leader import Researcher
import asyncio
from typing import Dict
from datetime import datetime
import re

class DRGenerator:
    """
    MetaGPT Deep Research生成器
    直接生成可发布的深度文章
    """

    def __init__(self):
        self.researcher = Researcher()
        self.researcher.rc.env = MGXEnv()

    async def generate_article(self, topic: Dict) -> str:
        """
        使用DR生成深度研究文章

        Input: trending topic dict
        Output: Markdown格式的完整文章
        """
        # 构建研究query
        query = self._build_research_query(topic)

        print(f"  → Generating DR for: {topic['title'][:50]}...")

        # 运行Deep Research
        await self.researcher.run(with_message=query)

        # 获取报告内容
        report_content = self.researcher.state.report_info["report_content"]

        # 添加frontmatter并格式化
        formatted_article = self._format_article(report_content, topic)

        return formatted_article

    def _build_research_query(self, topic: Dict) -> str:
        """
        构建DR查询prompt
        让DR生成符合我们需求的深度文章
        """
        query = f"""
深度研究主题：{topic['title']}

研究要求：
1. 生成一篇1000-1500字的深度分析文章
2. 包含技术细节、行业影响、未来展望
3. 引用权威数据源和最新信息
4. 适合技术和运营团队阅读
5. 结构清晰，论述有力

参考来源：{topic.get('url', '')}
话题类别：{topic.get('category', '科技')}
"""
        return query

    def _format_article(self, report: str, topic: Dict) -> str:
        """
        格式化DR报告为标准Markdown文章
        添加必要的元数据
        """
        # 生成slug（URL友好的标题）
        slug = self._generate_slug(topic['title'])

        # 提取或生成摘要（取前150字）
        excerpt = self._extract_excerpt(report)

        # 构建frontmatter
        frontmatter = f"""---
title: "{topic['title']}"
date: {datetime.now().strftime('%Y-%m-%d')}
time: {datetime.now().strftime('%H:%M:%S')}
slug: {slug}
source: {topic['source']}
source_url: {topic.get('url', '')}
engagement_score: {topic['engagement_score']}
category: {topic.get('category', '科技')}
tags: {self._extract_tags(topic)}
excerpt: "{excerpt}"
status: published
---"""

        # 组合最终文章
        return f"{frontmatter}\n\n{report}"

    def _generate_slug(self, title: str) -> str:
        """生成URL友好的slug"""
        # 移除特殊字符，转小写，空格变横线
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]  # 限制长度

    def _extract_excerpt(self, content: str) -> str:
        """提取文章摘要"""
        # 移除Markdown标记
        plain_text = re.sub(r'[#*`\[\]()]', '', content)
        # 取前150字
        return plain_text[:150].strip() + "..."

    def _extract_tags(self, topic: Dict) -> str:
        """根据标题和类别生成标签"""
        tags = []

        # 基于类别的标签
        if topic.get('category'):
            tags.append(topic['category'])

        # 基于关键词的标签
        title_lower = topic['title'].lower()
        tech_keywords = {
            'ai': 'AI', 'gpt': 'GPT', 'openai': 'OpenAI',
            'google': 'Google', 'apple': 'Apple', 'microsoft': 'Microsoft',
            'blockchain': '区块链', 'web3': 'Web3', 'crypto': '加密货币',
            'cloud': '云计算', 'database': '数据库', 'security': '安全'
        }

        for keyword, tag in tech_keywords.items():
            if keyword in title_lower:
                tags.append(tag)

        return str(tags[:5])  # 最多5个标签
```

### 4. Crawler Implementation

#### HackerNews Crawler (crawlers/hackernews.py)
```python
import aiohttp
from datetime import datetime
from .base_crawler import BaseCrawler

class HackerNewsCrawler(BaseCrawler):
    """
    HackerNews热门话题爬虫
    使用官方Firebase API，无需认证
    """

    API_BASE = "https://hacker-news.firebaseio.com/v0"

    async def fetch_trending(self) -> List[Dict]:
        """抓取HN热门话题"""
        trending_items = []

        async with aiohttp.ClientSession() as session:
            # 1. 获取热门故事ID列表
            async with session.get(f"{self.API_BASE}/topstories.json") as resp:
                story_ids = await resp.json()
                # 只取前30个
                story_ids = story_ids[:30]

            # 2. 并发获取每个故事的详情
            for story_id in story_ids:
                async with session.get(f"{self.API_BASE}/item/{story_id}.json") as resp:
                    story = await resp.json()

                    if story and story.get('title'):
                        item = {
                            'title': story['title'],
                            'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                            'source': 'hackernews',
                            'engagement_score': story.get('score', 0) + story.get('descendants', 0) * 0.5,
                            'published_at': datetime.fromtimestamp(story.get('time', 0)),
                            'category': self._categorize(story['title']),
                            'raw_data': story
                        }
                        trending_items.append(item)

        return trending_items

    def _categorize(self, title: str) -> str:
        """根据标题分类"""
        title_lower = title.lower()
        if any(kw in title_lower for kw in ['ai', 'gpt', 'llm', 'neural']):
            return 'AI'
        elif any(kw in title_lower for kw in ['blockchain', 'crypto', 'bitcoin']):
            return '区块链'
        elif any(kw in title_lower for kw in ['hack', 'security', 'vulnerability']):
            return '安全'
        else:
            return '科技'
```

### 5. Auto-Filter Configuration (config/filter_rules.yaml)

```yaml
# 自动筛选规则配置
# 运营团队可以调整这些规则来控制生成的内容类型

# 各平台最低热度要求
engagement_thresholds:
  hackernews: 100      # HN至少100个upvotes
  reddit: 500          # Reddit至少500 karma
  newsapi: 5000        # 新闻至少5000次分享

# 必须包含的关键词（至少一个）
topic_keywords:
  # 技术关键词
  tech:
    - AI
    - GPT
    - OpenAI
    - 人工智能
    - 机器学习
    - blockchain
    - 区块链
    - programming
    - 编程
    - software
    - 软件
    - cloud
    - 云计算
    - database
    - 数据库
    - security
    - 安全
    - DevOps
    - frontend
    - backend
    - algorithm
    - 算法

  # 新闻关键词
  news:
    - breakthrough  # 突破
    - 突破
    - announces     # 宣布
    - 发布
    - releases      # 发布
    - launches      # 推出
    - 推出
    - acquires      # 收购
    - 收购
    - funding       # 融资
    - 融资
    - IPO
    - partnership   # 合作
    - 合作

# 每天生成文章数量上限
daily_limit: 10

# 时效性要求
recency_hours: 24  # 只处理24小时内的trending

# 去重设置
deduplication:
  similarity_threshold: 0.85  # 标题相似度超过85%视为重复
  check_days: 7              # 检查最近7天是否已生成过类似内容
```

### 6. Main Pipeline (pipeline.py)

```python
#!/usr/bin/env python3
"""
TrendForge Pipeline - 自动化内容生成系统
"""

import asyncio
import argparse
from datetime import datetime
from pathlib import Path
import json
import yaml
import os
from typing import List, Dict

# Import all components
from crawlers.hackernews import HackerNewsCrawler
from crawlers.reddit import RedditCrawler
from crawlers.newsapi import NewsAPICrawler
from utils.filter import TrendingFilter
from utils.deduplicator import Deduplicator
from utils.storage import GitStorage
from generators.dr_generator import DRGenerator

class TrendForgePipeline:
    """主流水线控制器"""

    def __init__(self):
        print("Initializing TrendForge Pipeline...")

        # 初始化所有组件
        self.crawlers = [
            HackerNewsCrawler(),
            RedditCrawler(),
            NewsAPICrawler()
        ]
        self.filter = TrendingFilter()
        self.deduplicator = Deduplicator()
        self.dr_generator = DRGenerator()
        self.storage = GitStorage()

        # 确保目录存在
        self._ensure_directories()

    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            'data/trending',
            'data/processed',
            'content/blog',
            'logs'
        ]
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    async def run_daily_pipeline(self):
        """
        执行每日内容生成流程
        完整流程：抓取 → 去重 → 筛选 → DR生成 → 保存 → Git提交
        """
        start_time = datetime.now()
        print(f"\n{'='*60}")
        print(f"TrendForge Daily Pipeline - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        try:
            # Step 1: 抓取trending
            print("📡 Step 1: Fetching trending topics from all sources...")
            all_trending = await self._fetch_all_trending()
            print(f"   ✓ Fetched {len(all_trending)} total topics")

            # 保存原始trending数据
            self._save_raw_trending(all_trending)

            # Step 2: 去重
            print("\n🔍 Step 2: Deduplicating topics...")
            unique_trending = self.deduplicator.deduplicate(all_trending)
            print(f"   ✓ {len(unique_trending)} unique topics after deduplication")

            # Step 3: 自动筛选
            print("\n🎯 Step 3: Auto-filtering based on rules...")
            selected = self.filter.filter_trending(unique_trending)
            print(f"   ✓ Selected {len(selected)} topics for generation")

            if not selected:
                print("   ⚠️  No topics passed the filter criteria today")
                return

            # 显示选中的topics
            print("\n   Selected topics:")
            for i, topic in enumerate(selected, 1):
                print(f"   {i}. [{topic['source']}] {topic['title'][:60]}...")

            # 保存筛选后的数据
            self._save_processed_trending(selected)

            # Step 4: 使用DR生成深度文章
            print("\n📝 Step 4: Generating deep research articles with MetaGPT DR...")
            articles = await self._generate_articles(selected)
            print(f"   ✓ Successfully generated {len(articles)} articles")

            # Step 5: 保存文章
            print("\n💾 Step 5: Saving articles to content/blog/...")
            saved_files = self._save_articles(articles)
            print(f"   ✓ Saved {len(saved_files)} articles")

            # Step 6: Git提交
            print("\n📤 Step 6: Committing to Git...")
            commit_message = f"feat: add {len(articles)} new articles - {datetime.now().strftime('%Y-%m-%d')}"
            self.storage.commit_and_push(commit_message)
            print("   ✓ Committed and pushed to repository")

            # 完成
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            print(f"\n{'='*60}")
            print(f"✅ Pipeline completed successfully!")
            print(f"   Time taken: {duration:.1f} seconds")
            print(f"   Articles generated: {len(articles)}")
            print(f"{'='*60}\n")

        except Exception as e:
            print(f"\n❌ Pipeline failed with error: {e}")
            raise

    async def _fetch_all_trending(self) -> List[Dict]:
        """并发从所有源抓取trending"""
        tasks = []
        for crawler in self.crawlers:
            tasks.append(crawler.fetch_trending())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_items = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"   ⚠️  Crawler {i} failed: {result}")
            else:
                all_items.extend(result)

        return all_items

    async def _generate_articles(self, topics: List[Dict]) -> List[tuple]:
        """
        使用DR生成文章
        限制并发数量避免API过载
        """
        articles = []

        # 分批处理，每批3个（可配置）
        batch_size = 3
        for i in range(0, len(topics), batch_size):
            batch = topics[i:i+batch_size]
            print(f"\n   Processing batch {i//batch_size + 1}...")

            tasks = []
            for topic in batch:
                tasks.append(self.dr_generator.generate_article(topic))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for topic, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"   ⚠️  Failed to generate article for: {topic['title'][:50]}")
                    print(f"      Error: {result}")
                else:
                    articles.append((topic, result))
                    print(f"   ✓ Generated: {topic['title'][:50]}...")

        return articles

    def _save_articles(self, articles: List[tuple]) -> List[str]:
        """保存文章到content/blog/"""
        saved_files = []
        date_str = datetime.now().strftime('%Y-%m-%d')

        for topic, content in articles:
            # 生成文件名
            slug = self._generate_slug(topic['title'])
            filename = f"{date_str}-{slug}.md"
            filepath = Path(f"content/blog/{filename}")

            # 写入文件
            filepath.write_text(content, encoding='utf-8')
            saved_files.append(str(filepath))

            print(f"   💾 {filename}")

        return saved_files

    def _generate_slug(self, title: str) -> str:
        """生成URL友好的文件名"""
        import re
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]

    def _save_raw_trending(self, items: List[Dict]):
        """保存原始trending数据供分析"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        filepath = Path(f"data/trending/{date_str}.json")

        data = {
            'date': date_str,
            'timestamp': datetime.now().isoformat(),
            'count': len(items),
            'items': items
        }

        filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str))

    def _save_processed_trending(self, items: List[Dict]):
        """保存筛选后的数据"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        filepath = Path(f"data/processed/{date_str}.json")

        data = {
            'date': date_str,
            'timestamp': datetime.now().isoformat(),
            'count': len(items),
            'items': items
        }

        filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str))

def main():
    """主入口"""
    parser = argparse.ArgumentParser(description='TrendForge Pipeline')
    parser.add_argument(
        'command',
        choices=['full', 'test', 'crawl'],
        help='Command to run'
    )

    args = parser.parse_args()

    # 初始化pipeline
    pipeline = TrendForgePipeline()

    if args.command == 'full':
        # 运行完整pipeline
        asyncio.run(pipeline.run_daily_pipeline())

    elif args.command == 'crawl':
        # 只运行爬虫测试
        async def test_crawl():
            items = await pipeline._fetch_all_trending()
            print(f"Fetched {len(items)} items")
            for item in items[:5]:
                print(f"- [{item['source']}] {item['title'][:50]}...")

        asyncio.run(test_crawl())

    elif args.command == 'test':
        # 运行测试
        print("Running tests...")
        # TODO: Add test implementation

if __name__ == "__main__":
    main()
```

### 7. Git Storage Utils (utils/storage.py)

```python
from git import Repo
from pathlib import Path
import os

class GitStorage:
    """Git操作工具类"""

    def __init__(self, repo_path='.'):
        """初始化Git仓库"""
        self.repo_path = Path(repo_path)

        try:
            self.repo = Repo(self.repo_path)
        except:
            print("Initializing git repository...")
            self.repo = Repo.init(self.repo_path)

    def commit_and_push(self, message: str):
        """提交并推送到远程仓库"""
        try:
            # 添加content目录的所有更改
            self.repo.index.add(['content/'])

            # 提交
            self.repo.index.commit(message)
            print(f"   ✓ Committed: {message}")

            # 推送到远程（如果配置了）
            if self.repo.remotes:
                origin = self.repo.remote('origin')
                origin.push()
                print("   ✓ Pushed to origin")
            else:
                print("   ⚠️  No remote configured, skipping push")

        except Exception as e:
            print(f"   ⚠️  Git operation failed: {e}")
```

### 8. Installation & Setup Script (setup.sh)

```bash
#!/bin/bash

echo "==================================="
echo "TrendForge Backend Setup"
echo "==================================="

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install MetaGPT
echo "Installing MetaGPT DR module..."
pip install git+ssh://git@gitlab.deepwisdomai.com/pub/MetaGPT.git@dr4run

# Setup configuration
echo "Setting up configuration files..."
if [ ! -f backend/config/api_config.yaml ]; then
    cp backend/config/api_config.yaml.template backend/config/api_config.yaml
    echo "⚠️  Please edit backend/config/api_config.yaml with your API keys"
fi

# Setup MetaGPT config
echo "Setting up MetaGPT configuration..."
mkdir -p ~/.metagpt
if [ ! -f ~/.metagpt/config2.yaml ]; then
    echo "⚠️  Please copy your MetaGPT config to ~/.metagpt/config2.yaml"
fi

# Create necessary directories
echo "Creating project directories..."
mkdir -p data/trending data/processed content/blog logs

# Test installation
echo ""
echo "Testing installation..."
python -c "import metagpt; print('✓ MetaGPT installed')"
python -c "import aiohttp; print('✓ Dependencies installed')"

echo ""
echo "==================================="
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/config/api_config.yaml with your API keys"
echo "2. Copy MetaGPT config to ~/.metagpt/config2.yaml"
echo "3. Run: python backend/pipeline.py full"
echo "==================================="
```

## Key Changes from Previous Version

1. **Removed blog_generator.py** - DR直接生成最终内容
2. **Simplified pipeline** - 去掉了DR→Blog转换步骤
3. **Cost reduction** - 不需要调用GPT-4，只用MetaGPT DR
4. **Better quality** - DR生成的深度研究文章质量更高

## Testing Instructions

1. **Test DR Connection First**:
```bash
python -c "
from metagpt.environment.mgx.mgx_env import MGXEnv
from metagpt.roles.dr.research_leader import Researcher
researcher = Researcher()
researcher.rc.env = MGXEnv()
print('DR initialized successfully')
"
```

2. **Test Crawlers**:
```bash
python backend/pipeline.py crawl
```

3. **Run Full Pipeline**:
```bash
python backend/pipeline.py full
```

## Expected Daily Output

每天自动生成5-10篇深度文章：
```
content/blog/
├── 2025-01-24-openai-releases-gpt5.md       (1200字深度分析)
├── 2025-01-24-nvidia-new-gpu-architecture.md (1500字技术解读)
├── 2025-01-24-google-quantum-breakthrough.md  (1000字行业影响)
└── ...
```

每篇文章包含：
- 深度技术分析
- 行业影响评估
- 数据和引用
- 未来展望
- 相关链接

## Success Metrics

- [ ] 每天自动运行，无需人工干预
- [ ] 生成5-10篇高质量深度文章
- [ ] 每篇文章1000-1500字
- [ ] 自动推送到Git触发网站更新
- [ ] 运营可直接在网站查看和使用
- [ ] 总执行时间 < 60分钟