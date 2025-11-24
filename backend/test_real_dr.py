#!/usr/bin/env python3
"""
Test Real MetaGPT Deep Research
测试真实的MetaGPT DR功能
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加backend路径
sys.path.insert(0, '/mnt/d/gitlab_deepwisdom/trendforge/backend')


async def test_real_dr():
    """测试真实的MetaGPT DR"""
    try:
        print("="*60)
        print("Testing Real MetaGPT Deep Research")
        print("="*60)

        # 尝试导入MetaGPT
        print("\n1. 检查MetaGPT安装...")
        from metagpt.roles.researcher import Researcher
        from metagpt.logs import logger
        print("✅ MetaGPT DR已成功安装！")

        # 创建Researcher实例
        print("\n2. 初始化Deep Research...")
        researcher = Researcher()
        print("✅ DR Researcher初始化成功")

        # 测试话题
        test_topics = [
            "OpenAI's new o1 model and its chain-of-thought reasoning capabilities",
            "The impact of AI agents on software development workflows in 2025"
        ]

        print("\n3. 生成深度研究文章...")
        for i, topic in enumerate(test_topics, 1):
            print(f"\n[{i}/{len(test_topics)}] 话题: {topic[:50]}...")
            print("   正在进行深度研究（预计30-60秒）...")

            start_time = datetime.now()

            # 调用DR生成文章
            result = await researcher.run(topic)

            elapsed = (datetime.now() - start_time).total_seconds()

            # 保存结果
            output_dir = Path("/mnt/d/gitlab_deepwisdom/trendforge/content/blog")
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_dr_test_{i}.md"
            filepath = output_dir / filename

            # 添加frontmatter
            frontmatter = f"""---
title: "{topic}"
date: {datetime.now().isoformat()}
source: dr_test
word_count: {len(result.split())}
generation_time: {elapsed:.1f}
model: real_dr
---

"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
                f.write(result)

            print(f"   ✅ 成功生成！")
            print(f"   - 字数: {len(result.split())} words")
            print(f"   - 耗时: {elapsed:.1f}秒")
            print(f"   - 保存: {filepath.name}")

            # 只生成第一篇进行测试
            break

        print("\n" + "="*60)
        print("✅ Real DR测试成功！")
        print("="*60)

        return True

    except ImportError as e:
        print(f"\n❌ MetaGPT DR未安装或安装失败")
        print(f"   错误: {e}")
        print("\n请确保已执行:")
        print("pip install git+ssh://git@gitlab.deepwisdomai.com/pub/MetaGPT.git@dr4run")
        return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mock_fallback():
    """如果真实DR不可用，测试Mock模式"""
    print("\n使用Mock模式作为后备方案...")

    from dr_generator import DRGenerator

    generator = DRGenerator()
    test_item = {
        'title': 'Test: AI Development Tools Evolution',
        'source': 'test',
        'url': 'https://example.com',
        'engagement_score': 100
    }

    filepath = await generator.generate_article(test_item)
    if filepath:
        print(f"✅ Mock模式正常: {filepath}")
        return True
    return False


async def main():
    """主测试流程"""
    # 先尝试真实DR
    success = await test_real_dr()

    # 如果失败，使用Mock模式
    if not success:
        await test_mock_fallback()

    print("\n前端访问地址: http://localhost:3001")
    print("查看生成的文章！")


if __name__ == "__main__":
    asyncio.run(main())