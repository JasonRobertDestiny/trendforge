"""HackerNews 热点爬虫。"""
from __future__ import annotations

import aiohttp
from datetime import datetime
from typing import Dict, List

from .base_crawler import BaseCrawler

HN_TOP_LIMIT = 30  # 只取前 30 个热门
COMMENT_WEIGHT = 0.5  # 评论折算权重


class HackerNewsCrawler(BaseCrawler):
    """使用官方 Firebase API 拉取 HN 热榜。"""

    api_base = "https://hacker-news.firebaseio.com/v0"

    async def fetch_trending(self) -> List[Dict]:
        """抓取热门话题，返回统一结构。"""
        trending_items: List[Dict] = []

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base}/topstories.json") as resp:
                story_ids = await resp.json()
                top_ids = story_ids[:HN_TOP_LIMIT]

            # 顺序请求，避免过多并发对接口造成压力
            for story_id in top_ids:
                async with session.get(f"{self.api_base}/item/{story_id}.json") as resp:
                    story = await resp.json()

                if not story or not story.get("title"):
                    continue

                title = story["title"]
                score = story.get("score", 0)
                comments = story.get("descendants", 0)
                published_at = BaseCrawler.parse_datetime(story.get("time", datetime.now().timestamp()))

                item = {
                    "title": title,
                    "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    "source": "hackernews",
                    "engagement_score": score + comments * COMMENT_WEIGHT,
                    "published_at": published_at,
                    "category": self._categorize(title),
                    "raw_data": story,
                }
                trending_items.append(item)

        return trending_items

    @staticmethod
    def _categorize(title: str) -> str:
        """基于标题关键词粗略分类。"""
        lower = title.lower()
        if any(kw in lower for kw in ["ai", "gpt", "llm", "neural"]):
            return "AI"
        if any(kw in lower for kw in ["blockchain", "crypto", "bitcoin"]):
            return "区块链"
        if any(kw in lower for kw in ["hack", "security", "vulnerability"]):
            return "安全"
        return "科技"
