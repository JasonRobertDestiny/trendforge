#!/usr/bin/env python3
"""
测试单个爬虫模块
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.crawlers.hackernews import HackerNewsCrawler

async def test_hackernews():
    crawler = HackerNewsCrawler()
    items = await crawler.fetch_trending()
    print(f"获取了 {len(items)} 个HackerNews项目")
    for item in items[:3]:
        print(f"- {item.get('title', '')[:60]}... (score: {item.get('engagement_score', 0)})")
    return items

if __name__ == "__main__":
    asyncio.run(test_hackernews())