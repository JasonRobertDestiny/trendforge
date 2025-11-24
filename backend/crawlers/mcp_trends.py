"""基于 MCP Trends Hub 的聚合爬虫。"""
from __future__ import annotations

import aiohttp
from datetime import datetime
from typing import Dict, List

from .base_crawler import BaseCrawler

DEFAULT_MCP_BASE = "http://localhost:3000"
PLATFORMS = [
    "github",
    "hackernews",
    "producthunt",
    "reddit",
    "twitter",
    "weibo",
    "zhihu",
    "juejin",
    "baidu",
    "toutiao",
]


class MCPTrendsCrawler(BaseCrawler):
    """通过本地 MCP 服务拉取多平台 trending。"""

    def __init__(self, base_url: str = DEFAULT_MCP_BASE, limit: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.limit = limit

    async def fetch_trending(self) -> List[Dict]:
        all_items: List[Dict] = []
        for platform in PLATFORMS:
            try:
                items = await self._fetch_platform(platform)
                all_items.extend(items)
            except Exception as exc:  # pragma: no cover - 运行时容错
                print(f"   ⚠️  MCP {platform} 拉取失败: {exc}")
                continue
        return all_items

    async def _fetch_platform(self, platform: str) -> List[Dict]:
        url = f"{self.base_url}/trends/{platform}"
        payload = {"limit": self.limit}
        items: List[Dict] = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"status {resp.status}")
                data = await resp.json()

        for raw in data.get("items", []):
            title = raw.get("title")
            if not title:
                continue

            items.append(
                {
                    "title": title,
                    "url": raw.get("url", ""),
                    "source": platform,
                    "engagement_score": self._calculate_score(raw, platform),
                    "published_at": datetime.now(),  # MCP 端未必含时间，默认当前
                    "category": self._categorize(title),
                    "raw_data": raw,
                }
            )
        return items

    @staticmethod
    def _calculate_score(item: Dict, platform: str) -> float:
        """按平台差异化计算 engagement。"""
        platform = platform.lower()
        if platform == "github":
            return item.get("stars", 0) + item.get("forks", 0) * 2
        if platform == "hackernews":
            return item.get("points", 0) + item.get("comments", 0) * 0.5
        if platform == "reddit":
            return item.get("upvotes", 0) + item.get("comments", 0) * 0.3
        if platform == "weibo":
            return item.get("hot_value", 0)
        if platform == "zhihu":
            return item.get("hot_score", 0)
        if platform == "producthunt":
            return item.get("upvotes", 0)
        return item.get("score", 0) or item.get("likes", 0) or 0

    @staticmethod
    def _categorize(title: str) -> str:
        """粗分类，优先科技相关。"""
        lower = title.lower()
        if any(kw in lower for kw in ["ai", "gpt", "ml", "neural", "人工智能", "机器学习"]):
            return "AI"
        if any(kw in lower for kw in ["blockchain", "区块链", "crypto", "web3"]):
            return "区块链"
        if any(kw in lower for kw in ["security", "漏洞", "攻击", "breach"]):
            return "安全"
        return "科技"
