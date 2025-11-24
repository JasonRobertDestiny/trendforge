# TrendForge Backend - Updated Implementation with MCP Trends Hub

## 两种实现方案

### 方案A：使用 MCP Trends Hub（推荐）

如果在支持MCP的环境（如Claude Code），可以直接使用mcp-trends-hub获取多平台trending数据。

#### 1. 安装 MCP Trends Hub

```bash
# 全局安装
npm install -g mcp-trends-hub

# 或者作为项目依赖
npm install mcp-trends-hub

# 直接运行
npx -y mcp-trends-hub@1.6.2
```

#### 2. MCP 配置 (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "trends-hub": {
      "command": "npx",
      "args": ["-y", "mcp-trends-hub@1.6.2"]
    }
  }
}
```

#### 3. Python 调用 MCP（通过HTTP接口）

```python
# backend/crawlers/mcp_trends.py
import requests
import json
from typing import List, Dict
from datetime import datetime

class MCPTrendsCrawler:
    """
    使用MCP Trends Hub获取多平台trending
    """

    def __init__(self):
        # MCP服务器地址（根据实际配置）
        self.base_url = "http://localhost:3000"  # MCP server endpoint

    async def fetch_all_trending(self) -> List[Dict]:
        """
        获取所有平台的trending数据
        """
        platforms = [
            'github',
            'hackernews',
            'producthunt',
            'reddit',
            'twitter',
            'weibo',      # 微博
            'zhihu',      # 知乎
            'juejin',     # 掘金
            'baidu',      # 百度
            'toutiao',    # 今日头条
        ]

        all_trending = []

        for platform in platforms:
            try:
                trending = await self._fetch_platform_trending(platform)
                all_trending.extend(trending)
            except Exception as e:
                print(f"Failed to fetch {platform}: {e}")
                continue

        return all_trending

    async def _fetch_platform_trending(self, platform: str) -> List[Dict]:
        """
        获取单个平台的trending
        """
        # 调用MCP Trends Hub API
        response = requests.post(
            f"{self.base_url}/trends/{platform}",
            json={"limit": 30}
        )

        if response.status_code != 200:
            raise Exception(f"API returned {response.status_code}")

        data = response.json()

        # 转换为统一格式
        items = []
        for item in data.get('items', []):
            formatted = {
                'title': item.get('title'),
                'url': item.get('url'),
                'source': platform,
                'engagement_score': self._calculate_score(item, platform),
                'published_at': datetime.now(),  # MCP可能不提供时间
                'category': self._categorize(item.get('title', '')),
                'raw_data': item
            }
            items.append(formatted)

        return items

    def _calculate_score(self, item: Dict, platform: str) -> int:
        """
        计算统一的engagement分数
        """
        if platform == 'github':
            return item.get('stars', 0) + item.get('forks', 0) * 2
        elif platform == 'hackernews':
            return item.get('points', 0) + item.get('comments', 0) * 0.5
        elif platform == 'reddit':
            return item.get('upvotes', 0) + item.get('comments', 0) * 0.3
        elif platform == 'weibo':
            return item.get('hot_value', 0)  # 微博热度值
        elif platform == 'zhihu':
            return item.get('hot_score', 0)   # 知乎热度分
        else:
            return item.get('score', 0) or item.get('likes', 0) or 0
```

### 方案B：直接调用各平台API（Codex开发用）

保持原有设计，但增加更多数据源：

#### 1. 增强的爬虫实现

```python
# backend/crawlers/enhanced_crawlers.py

class GitHubTrendingCrawler(BaseCrawler):
    """
    GitHub Trending (使用非官方API)
    """
    API_URL = "https://github-trending-api.waningflow.com/repositories"

    async def fetch_trending(self) -> List[Dict]:
        params = {
            'language': '',  # All languages
            'since': 'daily',
            'spoken_language_code': 'zh'  # 包含中文项目
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_URL, params=params) as resp:
                data = await resp.json()

                items = []
                for repo in data[:30]:  # Top 30
                    item = {
                        'title': f"{repo['name']}: {repo.get('description', '')}",
                        'url': repo['url'],
                        'source': 'github',
                        'engagement_score': repo.get('stars', 0) + repo.get('forks', 0) * 2,
                        'published_at': datetime.now(),
                        'category': 'Development',
                        'raw_data': repo
                    }
                    items.append(item)

        return items


class ProductHuntCrawler(BaseCrawler):
    """
    Product Hunt trending products
    """
    async def fetch_trending(self) -> List[Dict]:
        # Product Hunt API需要token，可以用爬虫替代
        url = "https://www.producthunt.com/topics/artificial-intelligence"

        # 简化实现：解析HTML
        # 实际实现需要BeautifulSoup
        pass


class TwitterTrendsCrawler(BaseCrawler):
    """
    Twitter Trends via RapidAPI
    """
    def __init__(self, rapidapi_key: str):
        self.headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "twitter-api66.p.rapidapi.com"
        }

    async def fetch_trending(self) -> List[Dict]:
        url = "https://twitter-api66.p.rapidapi.com/trends/trending"

        params = {
            "woeid": "1",  # Worldwide
            "count": "50"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as resp:
                data = await resp.json()
                # Process Twitter trends
                pass
```

#### 2. 优化的过滤规则（包含中文内容）

```yaml
# backend/config/filter_rules.yaml
engagement_thresholds:
  hackernews: 100
  reddit: 500
  github: 50        # Stars
  weibo: 1000000    # 微博热度值
  zhihu: 10000      # 知乎热度
  producthunt: 100  # Upvotes

topic_keywords:
  # 英文技术关键词
  tech_en:
    - AI
    - GPT
    - OpenAI
    - blockchain
    - cryptocurrency
    - machine learning
    - cloud computing
    - DevOps
    - Kubernetes
    - microservices

  # 中文技术关键词
  tech_zh:
    - 人工智能
    - 机器学习
    - 深度学习
    - 区块链
    - 云计算
    - 大数据
    - 物联网
    - 5G
    - 量子计算

  # 新闻动态关键词
  news_keywords:
    - announces
    - launches
    - releases
    - acquires
    - funding
    - IPO
    - 发布
    - 推出
    - 收购
    - 融资
    - 上市

# 平台权重（某些平台的trending更有价值）
platform_weights:
  hackernews: 1.5    # HN的内容质量高
  github: 1.3        # 开源项目重要
  producthunt: 1.2   # 新产品发现
  reddit: 1.0
  twitter: 0.8       # 噪音较多
  weibo: 0.7         # 需要筛选
  zhihu: 1.1         # 深度内容

daily_limit: 10
recency_hours: 24
```

#### 3. 混合使用策略

```python
# backend/pipeline.py
class TrendForgePipeline:
    def __init__(self, use_mcp=False):
        if use_mcp and self._check_mcp_available():
            # 使用MCP Trends Hub
            self.crawlers = [MCPTrendsCrawler()]
        else:
            # 使用独立爬虫
            self.crawlers = [
                HackerNewsCrawler(),
                RedditCrawler(),
                GitHubTrendingCrawler(),
                # NewsAPICrawler(),  # 需要API key
                # TwitterTrendsCrawler(rapidapi_key),  # 需要RapidAPI key
            ]

    def _check_mcp_available(self):
        """检查MCP服务是否可用"""
        try:
            response = requests.get("http://localhost:3000/health")
            return response.status_code == 200
        except:
            return False
```

### 简化的快速启动方案（使用免费API）

如果想快速开始，只使用完全免费、无需认证的API：

```python
# backend/crawlers/free_crawlers.py

class FreeAPIsCrawler:
    """
    只使用免费、无需认证的API
    """

    async def fetch_all_free_trending(self):
        trending = []

        # 1. HackerNews - 完全免费
        hn_items = await self.fetch_hackernews()
        trending.extend(hn_items)

        # 2. Reddit - JSON端点免费
        reddit_items = await self.fetch_reddit_json()
        trending.extend(reddit_items)

        # 3. GitHub Trending - 非官方API免费
        github_items = await self.fetch_github_trending()
        trending.extend(github_items)

        return trending

    async def fetch_hackernews(self):
        """HackerNews官方API"""
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        # ... 实现

    async def fetch_reddit_json(self):
        """Reddit JSON端点（无需认证）"""
        subreddits = ['technology', 'programming', 'machinelearning']
        items = []

        for sub in subreddits:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=10"
            # 不需要API key，直接请求
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'User-Agent': 'TrendForge/1.0'}) as resp:
                    data = await resp.json()
                    # 处理Reddit数据
                    posts = data['data']['children']
                    # ...

        return items

    async def fetch_github_trending(self):
        """GitHub trending（非官方API）"""
        url = "https://github-trending-api.waningflow.com/repositories?since=daily"
        # ... 实现
```

## 更新后的成本分析

### 使用免费API的成本

```
必需付费项：
- MetaGPT DR调用: ~$150/月（10篇/天）

可选付费项：
- News API: $0（免费层1000次/月，可选）
- RapidAPI (Twitter): $0-10/月（可选）
- 其他全部免费

总成本: ~$150/月（只有DR是必需的）
```

### 数据源优先级建议

1. **核心数据源**（免费、高质量）：
   - HackerNews ⭐⭐⭐⭐⭐
   - GitHub Trending ⭐⭐⭐⭐⭐
   - Reddit Tech Subs ⭐⭐⭐⭐

2. **补充数据源**（增加覆盖面）：
   - Product Hunt ⭐⭐⭐
   - Twitter Trends ⭐⭐⭐
   - News API ⭐⭐⭐

3. **中文数据源**（如果需要）：
   - 知乎热榜
   - 微博热搜
   - 掘金热门

## 实施建议

1. **MVP阶段**：只用HackerNews + GitHub + Reddit（全免费）
2. **优化阶段**：加入mcp-trends-hub获取更多平台数据
3. **扩展阶段**：根据内容质量反馈，调整数据源权重

这样可以从零成本（除了DR）开始，逐步优化数据源。