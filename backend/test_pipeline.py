#!/usr/bin/env python3
"""
TrendForge Pipeline Test - 简化版测试脚本
测试完整的内容生成流程，不依赖未安装的模块
"""

import asyncio
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, '/mnt/d/gitlab_deepwisdom/trendforge/backend')

# 导入我们已经创建的DR生成器
from dr_generator import DRGenerator


class SimplePipeline:
    """简化版Pipeline，用于测试"""

    def __init__(self):
        self.dr_generator = DRGenerator(output_dir="/mnt/d/gitlab_deepwisdom/trendforge/content/blog")
        self.filter_config = {
            'min_score': {
                'hackernews': 100,
                'reddit': 500,
                'github': 30
            },
            'keywords': ['AI', 'GPT', 'OpenAI', 'Machine Learning', 'Cloud', 'Database',
                        'JavaScript', 'Python', 'React', 'API', 'framework', 'release']
        }

    def fetch_hackernews_trending(self) -> List[Dict]:
        """获取HackerNews热门话题"""
        print("\n📡 Fetching HackerNews trending...")
        items = []

        try:
            # 获取top stories
            response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
            story_ids = response.json()[:20]  # 获取前20个

            # 获取每个story的详情（只取前5个避免太慢）
            for story_id in story_ids[:5]:
                try:
                    story_resp = requests.get(
                        f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                        timeout=5
                    )
                    story = story_resp.json()

                    if story and story.get('title'):
                        item = {
                            'title': story.get('title', ''),
                            'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                            'source': 'hackernews',
                            'engagement_score': story.get('score', 0),
                            'comments': story.get('descendants', 0),
                            'author': story.get('by', 'unknown')
                        }
                        items.append(item)
                        print(f"  ✓ {item['title'][:60]}... (score: {item['engagement_score']})")

                except Exception as e:
                    print(f"  ⚠ Skip story {story_id}: {e}")
                    continue

        except Exception as e:
            print(f"  ✗ HackerNews error: {e}")

        return items

    def filter_items(self, items: List[Dict]) -> List[Dict]:
        """过滤高质量内容"""
        print(f"\n🔍 Filtering {len(items)} items...")
        filtered = []

        for item in items:
            source = item.get('source')
            score = item.get('engagement_score', 0)
            title = item.get('title', '').lower()

            # 检查分数阈值
            min_score = self.filter_config['min_score'].get(source, 100)
            if score < min_score:
                continue

            # 检查关键词
            has_keyword = any(kw.lower() in title for kw in self.filter_config['keywords'])
            if not has_keyword:
                continue

            filtered.append(item)
            print(f"  ✓ Passed: {item['title'][:50]}... (score: {score})")

        return filtered

    async def generate_articles(self, items: List[Dict]) -> List[str]:
        """生成DR文章"""
        print(f"\n📝 Generating {len(items)} articles...")
        articles = []

        for i, item in enumerate(items, 1):
            print(f"\n[{i}/{len(items)}] {item['title'][:60]}...")
            try:
                filepath = await self.dr_generator.generate_article(item)
                if filepath:
                    articles.append(filepath)
            except Exception as e:
                print(f"  ✗ Generation failed: {e}")

        return articles

    def save_summary(self, trending_items: List[Dict], articles: List[str]):
        """保存执行摘要"""
        logs_dir = Path("/mnt/d/gitlab_deepwisdom/trendforge/logs")
        logs_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = logs_dir / f"pipeline_run_{timestamp}.json"

        summary = {
            'timestamp': datetime.now().isoformat(),
            'trending_found': len(trending_items),
            'articles_generated': len(articles),
            'success_rate': f"{len(articles)/max(len(trending_items), 1)*100:.1f}%",
            'items_processed': trending_items,
            'articles_created': articles
        }

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n✓ Summary saved: {summary_file}")

    async def run(self):
        """运行Pipeline"""
        print("="*70)
        print(f"TrendForge Pipeline Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        # 1. 获取trending
        trending_items = self.fetch_hackernews_trending()

        if not trending_items:
            print("\n⚠ No trending items found")
            return

        # 2. 过滤
        filtered_items = self.filter_items(trending_items)

        if not filtered_items:
            print("\n⚠ No items passed the filter")
            # 降低阈值重试
            print("\n🔄 Retrying with lower thresholds...")
            self.filter_config['min_score']['hackernews'] = 50
            filtered_items = self.filter_items(trending_items)

        if not filtered_items:
            print("\n⚠ Still no items passed, check filter config")
            return

        # 3. 生成文章（最多3篇，避免太慢）
        articles_to_generate = filtered_items[:3]
        articles = await self.generate_articles(articles_to_generate)

        # 4. 保存摘要
        self.save_summary(articles_to_generate, articles)

        # 5. 报告
        print("\n" + "="*70)
        print("Pipeline Complete")
        print("="*70)
        print(f"📊 Trending found: {len(trending_items)}")
        print(f"🎯 Passed filter: {len(filtered_items)}")
        print(f"📝 Articles generated: {len(articles)}")
        print(f"✅ Success rate: {len(articles)/max(len(articles_to_generate), 1)*100:.1f}%")

        if articles:
            print("\n📚 Generated articles:")
            for article in articles:
                print(f"  - {Path(article).name}")


async def main():
    """主函数"""
    pipeline = SimplePipeline()
    await pipeline.run()


if __name__ == "__main__":
    # 运行pipeline
    asyncio.run(main())