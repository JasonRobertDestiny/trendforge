#!/usr/bin/env python3
"""
MetaGPT Deep Research Generator
使用MetaGPT DR生成深度文章
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import re
import yaml

class DRGenerator:
    """
    MetaGPT Deep Research文章生成器
    """

    def __init__(self, output_dir: str = "../content/blog"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.researcher = None
        self._init_researcher()

    def _init_researcher(self):
        """初始化DR研究员"""
        try:
            from metagpt.roles.researcher import Researcher
            self.researcher = Researcher()
            print("✓ MetaGPT DR initialized")
        except ImportError:
            print("⚠ MetaGPT not installed, using mock mode")
            self.researcher = None

    async def generate_article(self, trending_item: Dict) -> Optional[str]:
        """
        为trending项目生成深度文章

        Args:
            trending_item: 包含title, source, url等信息的dict

        Returns:
            生成的文章路径，失败返回None
        """
        title = trending_item.get('title', '')
        source = trending_item.get('source', 'unknown')

        # 构建DR查询prompt
        dr_prompt = self._build_dr_prompt(trending_item)

        print(f"\n生成文章: {title}")
        print(f"来源: {source}")

        # 生成文章内容
        if self.researcher:
            content = await self._generate_with_dr(dr_prompt)
        else:
            content = self._generate_mock(dr_prompt, title)

        if not content:
            print(f"✗ 生成失败: {title}")
            return None

        # 保存文章
        filepath = self._save_article(trending_item, content)
        print(f"✓ 文章已保存: {filepath}")

        return str(filepath)

    def _build_dr_prompt(self, item: Dict) -> str:
        """
        构建DR查询prompt
        """
        title = item.get('title', '')
        description = item.get('description', '')
        url = item.get('url', '')

        # 构建深度研究提示
        prompt = f"""
请对以下热门话题进行深度研究和分析：

标题：{title}

{f'描述：{description}' if description else ''}
{f'参考链接：{url}' if url else ''}

请提供以下内容：
1. 背景介绍和重要性分析
2. 技术细节或关键要点深度解析
3. 行业影响和未来趋势预测
4. 实际应用场景和案例
5. 潜在挑战和解决方案

文章要求：
- 字数：1000-1500字
- 风格：专业、深入、易读
- 目标读者：技术决策者和行业从业者
"""
        return prompt.strip()

    async def _generate_with_dr(self, prompt: str) -> Optional[str]:
        """
        使用真实DR生成文章
        """
        try:
            print("正在生成深度文章（预计30-60秒）...")
            result = await self.researcher.run(prompt)

            # 确保文章有合适的格式
            if not result.startswith('#'):
                # 添加标题
                lines = prompt.split('\n')
                title_line = next((l for l in lines if '标题：' in l), '')
                title = title_line.replace('标题：', '').strip() if title_line else 'Research Article'
                result = f"# {title}\n\n{result}"

            return result

        except Exception as e:
            print(f"DR生成错误: {e}")
            return None

    def _generate_mock(self, prompt: str, title: str) -> str:
        """
        模拟生成（用于测试）
        """
        print("使用模拟模式生成...")

        # 从prompt提取标题
        clean_title = title.split(':')[0] if ':' in title else title

        mock_content = f"""# {clean_title}

## 背景介绍

{clean_title}代表了当前技术发展的重要方向。这一发展不仅影响技术领域，更将深刻改变我们的工作和生活方式。

## 核心技术解析

### 技术架构

该技术采用了创新的架构设计，主要包括以下几个关键组件：

1. **核心引擎**：负责主要计算和处理逻辑
2. **数据层**：提供高效的数据存储和访问
3. **接口层**：支持多种集成方式和扩展能力

### 关键创新

这项技术的主要创新点在于：

- 突破性的性能提升
- 更加友好的用户体验
- 强大的扩展性和兼容性

## 行业影响

### 短期影响

在未来6-12个月内，我们将看到：

1. 早期采用者开始试点应用
2. 行业标准逐步形成
3. 相关生态系统快速发展

### 长期趋势

从长远来看，这项技术将：

- 重新定义行业标准
- 催生新的商业模式
- 推动相关领域的创新

## 实际应用场景

### 企业级应用

大型企业可以利用这项技术：

- 优化现有业务流程
- 提升运营效率
- 降低成本开支

### 创新应用

创业公司和创新团队可以：

- 快速构建原型
- 验证商业想法
- 加速产品迭代

## 挑战与机遇

### 主要挑战

1. **技术挑战**：需要解决的技术难题
2. **市场挑战**：用户接受度和市场教育
3. **监管挑战**：合规性和标准化问题

### 应对策略

针对这些挑战，建议采取以下策略：

- 加强技术研发投入
- 建立行业联盟和标准
- 积极与监管机构沟通

## 结论

{clean_title}标志着技术发展的新阶段。虽然面临诸多挑战，但其带来的机遇更加令人期待。企业和个人都应该密切关注这一趋势，及时调整策略，抓住发展机遇。

---
*本文通过深度研究分析生成，旨在为读者提供全面的行业洞察。*
"""
        return mock_content

    def _save_article(self, item: Dict, content: str) -> Path:
        """
        保存文章到文件
        """
        # 生成文件名
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        title_slug = self._slugify(item.get('title', 'article'))
        filename = f"{date_str}_{title_slug}.md"

        # 创建frontmatter
        frontmatter = {
            'title': item.get('title', 'Untitled'),
            'date': datetime.now().isoformat(),
            'source': item.get('source', 'unknown'),
            'engagement_score': item.get('engagement_score', 0),
            'url': item.get('url', ''),
            'tags': self._extract_tags(item),
            'word_count': len(content.split())
        }

        # 组合文件内容
        file_content = "---\n"
        file_content += yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
        file_content += "---\n\n"
        file_content += content

        # 保存文件
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)

        return filepath

    def _slugify(self, text: str) -> str:
        """
        将文本转换为URL友好的slug
        """
        # 移除特殊字符，保留字母数字和空格
        text = re.sub(r'[^\w\s-]', '', text.lower())
        # 替换空格为下划线
        text = re.sub(r'[-\s]+', '_', text)
        # 限制长度
        return text[:50]

    def _extract_tags(self, item: Dict) -> list:
        """
        从内容提取标签
        """
        tags = []

        # 添加来源标签
        if item.get('source'):
            tags.append(item['source'])

        # 从标题提取关键词
        title = item.get('title', '')
        tech_keywords = ['AI', 'GPT', 'API', 'Cloud', 'Database', 'JavaScript',
                        'Python', 'React', 'Machine Learning', 'Blockchain']

        for keyword in tech_keywords:
            if keyword.lower() in title.lower():
                tags.append(keyword)

        return tags[:5]  # 限制最多5个标签


async def test_dr_generator():
    """
    测试DR生成器
    """
    generator = DRGenerator(output_dir="/mnt/d/gitlab_deepwisdom/trendforge/content/blog")

    # 测试数据
    test_items = [
        {
            'title': 'GitHub Copilot Workspace: AI-Native Development Environment',
            'source': 'hackernews',
            'url': 'https://github.blog/copilot-workspace',
            'engagement_score': 450,
            'description': 'GitHub introduces Copilot Workspace, an AI-native development environment'
        },
        {
            'title': 'PostgreSQL 17 Released with Major Performance Improvements',
            'source': 'reddit',
            'url': 'https://www.postgresql.org/about/news/postgresql-17',
            'engagement_score': 320,
            'description': 'New version brings 2x query performance and improved JSON support'
        }
    ]

    for item in test_items:
        filepath = await generator.generate_article(item)
        if filepath:
            print(f"成功: {filepath}")
        else:
            print(f"失败: {item['title']}")


if __name__ == "__main__":
    print("="*60)
    print("Testing DR Generator")
    print("="*60)

    asyncio.run(test_dr_generator())