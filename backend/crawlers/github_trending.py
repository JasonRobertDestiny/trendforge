"""GitHub Trending 爬虫（使用 waningflow 非官方 API）。"""
from __future__ import annotations

import aiohttp
from datetime import datetime
from typing import Dict, List

from .base_crawler import BaseCrawler

API_URL = "https://github-trending-api.waningflow.com/repositories"
TOP_LIMIT = 30
FORK_WEIGHT = 2  # fork 权重


class GitHubTrendingCrawler(BaseCrawler):
    """拉取 GitHub Trending，每日榜单。"""

    async def fetch_trending(self) -> List[Dict]:
        params = {
            "since": "daily",
            "language": "",
            "spoken_language_code": "zh",
        }
        items: List[Dict] = []

        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params) as resp:
                data = await resp.json()

        for repo in data[:TOP_LIMIT]:
            title = f"{repo.get('name', '')}: {repo.get('description', '')}".strip()
            if not title:
                continue

            stars = repo.get("stars", 0)
            forks = repo.get("forks", 0)
            engagement = stars + forks * FORK_WEIGHT

            items.append(
                {
                    "title": title,
                    "url": repo.get("url", ""),
                    "source": "github",
                    "engagement_score": engagement,
                    "published_at": datetime.now(),
                    "category": "开发",  # 统一归类为开发/工程
                    "raw_data": repo,
                }
            )

        return items
