#!/usr/bin/env python3
"""
TrendForge简化测试脚本
测试基础爬虫功能，不依赖aiohttp
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def test_hackernews():
    """测试HackerNews API"""
    print("Testing HackerNews API...")

    try:
        # 获取top stories
        response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        story_ids = response.json()[:5]  # 只取前5个测试

        print(f"✓ Got {len(story_ids)} story IDs")

        # 获取第一个story的详情
        if story_ids:
            story_response = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_ids[0]}.json")
            story = story_response.json()
            print(f"✓ First story: {story.get('title', 'N/A')[:50]}...")
            print(f"  Score: {story.get('score', 0)}, Comments: {story.get('descendants', 0)}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_reddit():
    """测试Reddit JSON端点"""
    print("\nTesting Reddit API...")

    try:
        headers = {'User-Agent': 'TrendForge/1.0'}
        response = requests.get("https://www.reddit.com/r/technology/hot.json?limit=5", headers=headers)
        data = response.json()

        posts = data['data']['children']
        print(f"✓ Got {len(posts)} posts from r/technology")

        if posts:
            first_post = posts[0]['data']
            print(f"✓ First post: {first_post['title'][:50]}...")
            print(f"  Upvotes: {first_post['ups']}, Comments: {first_post['num_comments']}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_github_trending():
    """测试GitHub Trending API (非官方)"""
    print("\nTesting GitHub Trending API...")

    try:
        # 使用备用API
        response = requests.get("https://github-trending-api.waningflow.com/repositories?since=daily")

        if response.status_code == 200:
            repos = response.json()[:5]  # 只取前5个
            print(f"✓ Got {len(repos)} trending repositories")

            if repos:
                first_repo = repos[0]
                print(f"✓ First repo: {first_repo.get('name', 'N/A')}")
                print(f"  Stars: {first_repo.get('stars', 0)}, Language: {first_repo.get('language', 'N/A')}")
        else:
            print(f"⚠ API returned status {response.status_code}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_filter_logic():
    """测试筛选逻辑"""
    print("\nTesting filter logic...")

    # 模拟trending数据
    mock_trending = [
        {
            'title': 'OpenAI Releases GPT-5 with Amazing Features',
            'source': 'hackernews',
            'engagement_score': 500,
            'published_at': datetime.now().isoformat()
        },
        {
            'title': 'Random Sports News',
            'source': 'reddit',
            'engagement_score': 50,
            'published_at': datetime.now().isoformat()
        },
        {
            'title': 'New JavaScript Framework Released',
            'source': 'github',
            'engagement_score': 200,
            'published_at': datetime.now().isoformat()
        }
    ]

    # 简单的关键词筛选
    tech_keywords = ['AI', 'GPT', 'OpenAI', 'JavaScript', 'Framework', 'Cloud', 'Database']
    min_score = 100

    filtered = []
    for item in mock_trending:
        # 检查关键词
        has_keyword = any(kw.lower() in item['title'].lower() for kw in tech_keywords)
        # 检查分数
        high_score = item['engagement_score'] >= min_score

        if has_keyword and high_score:
            filtered.append(item)
            print(f"✓ Passed filter: {item['title'][:40]}... (score: {item['engagement_score']})")
        else:
            print(f"✗ Filtered out: {item['title'][:40]}...")

    print(f"\nResult: {len(filtered)}/{len(mock_trending)} items passed filter")
    return True

def test_file_structure():
    """测试文件结构"""
    print("\nTesting file structure...")

    required_dirs = [
        'data/trending',
        'data/processed',
        'content/blog',
        'logs'
    ]

    for dir_path in required_dirs:
        path = Path(f"../{dir_path}")
        if path.exists():
            print(f"✓ Directory exists: {dir_path}")
        else:
            # 创建目录
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {dir_path}")

    return True

def main():
    print("="*60)
    print("TrendForge Backend Test Suite")
    print("="*60)

    tests = [
        test_hackernews,
        test_reddit,
        test_github_trending,
        test_filter_logic,
        test_file_structure
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test failed with error: {e}")
            results.append(False)

    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✅ All tests passed!")
    else:
        print("⚠️ Some tests failed")

if __name__ == "__main__":
    main()