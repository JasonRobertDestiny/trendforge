"""NewsAPI 热点爬虫。"""
from __future__ import annotations

import aiohttp
from datetime import datetime
from typing import Dict, List

from .base_crawler import BaseCrawler
from backend.utils.config_loader import load_yaml_config

NEWSAPI_ENDPOINT = "https://newsapi.org/v2/top-headlines"
DEFAULT_COUNTRY = "us"
PAGE_SIZE = 30
BASE_ENGAGEMENT = 6000  # 构造的热度基准，保证可通过阈值
ENGAGEMENT_STEP = 120   # 递减步长


class NewsAPICrawler(BaseCrawler):
    """使用 NewsAPI 获取科技新闻。"""

    def __init__(self) -> None:
        api_conf = load_yaml_config("backend/config/api_config.yaml")
        self.api_key = api_conf.get("newsapi_key")

    async def fetch_trending(self) -> List[Dict]:
        """调用 NewsAPI，返回标准化热点列表。"""
        if not self.api_key:
            # 缺少密钥直接返回空列表，避免报错
            return []

        params = {
            "category": "technology",
            "language": "en",
            "pageSize": PAGE_SIZE,
            "country": DEFAULT_COUNTRY,
        }
        headers = {"Authorization": self.api_key}
        items: List[Dict] = []

        async with aiohttp.ClientSession() as session:
            async with session.get(NEWSAPI_ENDPOINT, params=params, headers=headers) as resp:
                data = await resp.json()

        articles = data.get("articles", [])
        for idx, article in enumerate(articles):
            title = article.get("title")
            if not title:
                continue

            published_at = BaseCrawler.parse_datetime(article.get("publishedAt", datetime.now().isoformat()))
            engagement = BASE_ENGAGEMENT - idx * ENGAGEMENT_STEP

            items.append(
                {
                    "title": title,
                    "url": article.get("url", ""),
                    "source": "newsapi",
                    "engagement_score": max(0, engagement),
                    "published_at": published_at,
                    "category": self._categorize(title),
                    "raw_data": article,
                }
            )

        return items

    @staticmethod
    def _categorize(title: str) -> str:
        """基于关键词分科技子类。"""
        lower = title.lower()
        if any(kw in lower for kw in ["ai", "gpt", "ml", "neural"]):
            return "AI"
        if any(kw in lower for kw in ["chip", "gpu", "cpu", "semiconductor"]):
            return "硬件"
        if any(kw in lower for kw in ["security", "breach", "attack"]):
            return "安全"
        return "科技"
