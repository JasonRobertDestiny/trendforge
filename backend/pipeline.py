#!/usr/bin/env python3
"""TrendForge 每日自动化管线。"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 添加父目录到路径以便正确导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from backend.crawlers.hackernews import HackerNewsCrawler
from backend.crawlers.reddit import RedditCrawler
from backend.crawlers.newsapi import NewsAPICrawler
from backend.crawlers.github_trending import GitHubTrendingCrawler
from backend.crawlers.mcp_trends import MCPTrendsCrawler
from backend.generators.dr_generator import DRGenerator
from backend.utils.config_loader import load_yaml_config
from backend.utils.deduplicator import Deduplicator
from backend.utils.filter import TrendingFilter
from backend.utils.storage import GitStorage

RAW_DATA_DIR = Path("data/trending")
PROCESSED_DATA_DIR = Path("data/processed")
CONTENT_DIR = Path("content/blog")
LOG_DIR = Path("logs")
DEFAULT_COMMIT_PREFIX = "feat: add"  # 保持提交信息格式一致


class TrendForgePipeline:
    """主流程控制器。"""

    def __init__(self, use_mcp: bool = False, mcp_base: str | None = None) -> None:
        dr_conf = load_yaml_config("backend/config/dr_config.yaml")
        self.batch_size = dr_conf.get("batch_size", 3)
        self.max_articles = dr_conf.get("max_articles_per_run", 10)

        self.crawlers = self._init_crawlers(use_mcp, mcp_base)
        self.filter = TrendingFilter()
        self.deduplicator = Deduplicator()
        self.dr_generator = DRGenerator()
        self.storage = GitStorage()

        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """确保运行所需目录存在。"""
        for folder in [RAW_DATA_DIR, PROCESSED_DATA_DIR, CONTENT_DIR, LOG_DIR]:
            folder.mkdir(parents=True, exist_ok=True)

    def _init_crawlers(self, use_mcp: bool, mcp_base: str | None) -> List:
        """根据开关选择爬虫列表。"""
        base = (mcp_base or "http://localhost:3001").rstrip("/")

        if use_mcp:
            if self._check_mcp_available(base):
                print(f"   ✓ 使用 MCP Trends Hub: {base}")
                return [MCPTrendsCrawler(base_url=base)]
            print("   ⚠️  MCP 未就绪，回退本地爬虫")

        print("   ℹ️ 使用本地独立爬虫")
        return [
            HackerNewsCrawler(),
            GitHubTrendingCrawler(),
            RedditCrawler(),
            NewsAPICrawler(),
        ]

    async def run_daily_pipeline(self) -> None:
        """完整流程：抓取 → 去重 → 筛选 → DR 生成 → 保存 → Git 提交。"""
        start_time = datetime.now()
        print("\n" + "=" * 60)
        print(f"TrendForge Daily Pipeline - {start_time:%Y-%m-%d %H:%M:%S}")
        print("=" * 60)

        try:
            print("📡 Step 1: Fetching trending topics...")
            all_trending = await self._fetch_all_trending()
            print(f"   ✓ Got {len(all_trending)} raw topics")

            self._save_raw_trending(all_trending)

            print("\n🔍 Step 2: Deduplicating...")
            unique_trending = self.deduplicator.deduplicate(all_trending)
            print(f"   ✓ {len(unique_trending)} unique after dedup")

            print("\n🎯 Step 3: Filtering...")
            selected = self.filter.filter_trending(unique_trending)
            if not selected:
                print("   ⚠️  No topics passed filter today")
                return

            if len(selected) > self.max_articles:
                selected = selected[: self.max_articles]

            for idx, topic in enumerate(selected, start=1):
                title_preview = topic["title"][:60]
                print(f"   {idx}. [{topic['source']}] {title_preview}")

            self._save_processed_trending(selected)

            print("\n📝 Step 4: Generating articles via DR...")
            articles = await self._generate_articles(selected)
            print(f"   ✓ Generated {len(articles)} articles")

            print("\n💾 Step 5: Saving markdown files...")
            saved_files = self._save_articles(articles)
            print(f"   ✓ Saved {len(saved_files)} files")

            print("\n📤 Step 6: Git commit & push...")
            commit_msg = f"{DEFAULT_COMMIT_PREFIX} {len(articles)} new articles - {datetime.now():%Y-%m-%d}"
            self.storage.commit_and_push(commit_msg)

            duration = (datetime.now() - start_time).total_seconds()
            print("\n" + "=" * 60)
            print("✅ Pipeline finished")
            print(f"耗时: {duration:.1f}s, 文章数: {len(articles)}")
            print("=" * 60)
        except Exception as exc:  # pragma: no cover - 运行时错误需直接暴露
            print(f"\n❌ Pipeline failed: {exc}")
            raise

    async def _fetch_all_trending(self) -> List[Dict]:
        """并发执行所有爬虫。"""
        tasks = [crawler.fetch_trending() for crawler in self.crawlers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        items: List[Dict] = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"   ⚠️  Crawler {idx} failed: {result}")
                continue
            items.extend(result)
        return items

    @staticmethod
    def _check_mcp_available(base_url: str) -> bool:
        """探测 MCP 服务健康接口。"""
        try:
            resp = requests.get(f"{base_url}/health", timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    async def _generate_articles(self, topics: List[Dict]) -> List[Tuple[Dict, str]]:
        """批量调用 DR，限制并发批次。"""
        articles: List[Tuple[Dict, str]] = []
        for start in range(0, len(topics), self.batch_size):
            batch = topics[start : start + self.batch_size]
            print(f"   → Batch {start // self.batch_size + 1} ({len(batch)} items)")

            tasks = [self.dr_generator.generate_article(topic) for topic in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for topic, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"   ⚠️  Fail: {topic['title'][:50]} -> {result}")
                    continue
                articles.append((topic, result))
                print(f"   ✓ Done: {topic['title'][:50]}")
        return articles

    def _save_articles(self, articles: List[Tuple[Dict, str]]) -> List[str]:
        """写入 Markdown 文件。"""
        saved: List[str] = []
        date_str = datetime.now().strftime("%Y-%m-%d")

        for topic, content in articles:
            slug = self._generate_slug(topic["title"])
            filename = f"{date_str}-{slug}.md"
            filepath = CONTENT_DIR / filename
            filepath.write_text(content, encoding="utf-8")
            saved.append(str(filepath))
        return saved

    @staticmethod
    def _generate_slug(title: str) -> str:
        """文件名专用 slug，保持与 DR 内部一致。"""
        import re

        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug[:50]

    def _save_raw_trending(self, items: List[Dict]) -> None:
        """保存原始抓取结果，便于分析与回溯。"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        payload = {
            "date": date_str,
            "timestamp": datetime.now().isoformat(),
            "count": len(items),
            "items": items,
        }
        (RAW_DATA_DIR / f"{date_str}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

    def _save_processed_trending(self, items: List[Dict]) -> None:
        """保存筛选后的结果。"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        payload = {
            "date": date_str,
            "timestamp": datetime.now().isoformat(),
            "count": len(items),
            "items": items,
        }
        (PROCESSED_DATA_DIR / f"{date_str}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="TrendForge Pipeline")
    parser.add_argument("command", choices=["full", "crawl", "test"], help="选择要执行的命令")
    parser.add_argument("--use-mcp", action="store_true", help="启用 MCP Trends Hub 数据源")
    parser.add_argument("--mcp-base", help="MCP 服务地址，默认 http://localhost:3001")
    args = parser.parse_args()

    pipeline = TrendForgePipeline(use_mcp=args.use_mcp, mcp_base=args.mcp_base)

    if args.command == "full":
        asyncio.run(pipeline.run_daily_pipeline())
    elif args.command == "crawl":
        asyncio.run(_run_crawl(pipeline))
    elif args.command == "test":
        print("暂无自动化测试，请手动执行 crawl/full 以验证。")


def _format_preview(item: Dict) -> str:
    """格式化打印预览文本。"""
    title = item.get("title", "")
    return f"[{item.get('source', '')}] {title[:80]}"


async def _run_crawl(pipeline: TrendForgePipeline) -> None:
    """只运行爬虫并打印部分结果。"""
    items = await pipeline._fetch_all_trending()
    print(f"Fetched {len(items)} items")
    for item in items[:5]:
        print("-", _format_preview(item))


if __name__ == "__main__":
    main()
