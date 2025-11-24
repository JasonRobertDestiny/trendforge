"""Reddit 热点爬虫（使用公开 JSON，无需 OAuth）。"""
from __future__ import annotations

import aiohttp
from datetime import datetime
from typing import Dict, List

from .base_crawler import BaseCrawler
from backend.utils.config_loader import load_yaml_config

REDDIT_URL = "https://www.reddit.com/r/technology/top.json?limit=30&t=day"
COMMENT_WEIGHT = 0.2  # 评论折算权重


class RedditCrawler(BaseCrawler):
    """抓取 /r/technology 日榜热点。"""

    def __init__(self) -> None:
        api_conf = load_yaml_config("backend/config/api_config.yaml")
        self.user_agent = api_conf.get("reddit_user_agent", "trendforge-bot/0.1")

    async def fetch_trending(self) -> List[Dict]:
        """拉取 Reddit 热点并标准化结构。"""
        headers = {"User-Agent": self.user_agent}
        items: List[Dict] = []

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(REDDIT_URL) as resp:
                data = await resp.json()

        posts = data.get("data", {}).get("children", [])
        for post in posts:
            info = post.get("data", {})
            title = info.get("title")
            if not title:
                continue

            ups = info.get("ups", 0)
            comments = info.get("num_comments", 0)
            published_at = BaseCrawler.parse_datetime(info.get("created_utc", datetime.now().timestamp()))

            item = {
                "title": title,
                "url": f"https://www.reddit.com{info.get('permalink', '')}",
                "source": "reddit",
                "engagement_score": ups + comments * COMMENT_WEIGHT,
                "published_at": published_at,
                "category": self._categorize(title),
                "raw_data": info,
            }
            items.append(item)

        return items

    @staticmethod
    def _categorize(title: str) -> str:
        """基于标题粗分科技子类。"""
        lower = title.lower()
        if any(kw in lower for kw in ["ai", "gpt", "llm", "neural"]):
            return "AI"
        if any(kw in lower for kw in ["cloud", "aws", "azure", "gcp"]):
            return "云计算"
        if any(kw in lower for kw in ["security", "breach", "vulnerability"]):
            return "安全"
        return "科技"
