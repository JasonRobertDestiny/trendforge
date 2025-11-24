"""MetaGPT Deep Research 文章生成器。"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, List

try:
    from metagpt.environment.mgx.mgx_env import MGXEnv
    from metagpt.roles.dr.research_leader import Researcher
except ImportError as exc:  # pragma: no cover - 环境缺模块时给出友好提示
    raise ImportError("请先安装 MetaGPT: pip install git+ssh://git@gitlab.deepwisdomai.com/pub/MetaGPT.git@dr4run") from exc

TAG_KEYWORDS = {
    "ai": "AI",
    "gpt": "GPT",
    "openai": "OpenAI",
    "google": "Google",
    "apple": "Apple",
    "microsoft": "Microsoft",
    "blockchain": "区块链",
    "web3": "Web3",
    "crypto": "加密货币",
    "cloud": "云计算",
    "database": "数据库",
    "security": "安全",
}
EXCERPT_LENGTH = 150
SLUG_MAX_LENGTH = 50


class DRGenerator:
    """封装 MetaGPT Deep Research，直接生成可发布 Markdown。"""

    def __init__(self) -> None:
        # 初始化 DR 角色与环境
        self.researcher = Researcher()
        self.researcher.rc.env = MGXEnv()

    async def generate_article(self, topic: Dict) -> str:
        """对单个话题生成深度文章。"""
        query = self._build_research_query(topic)

        print(f"  → 正在生成: {topic['title'][:50]}...")
        await self.researcher.run(with_message=query)

        report_content = self.researcher.state.report_info["report_content"]
        return self._format_article(report_content, topic)

    def _build_research_query(self, topic: Dict) -> str:
        """根据话题构造 DR 提示。"""
        return f"""
深度研究主题：{topic['title']}

研究要求：
1. 生成一篇1000-1500字的深度分析文章
2. 包含技术细节、行业影响、未来展望
3. 引用权威数据源和最新信息
4. 适合技术和运营团队阅读
5. 结构清晰，论述有力

参考来源：{topic.get('url', '')}
话题类别：{topic.get('category', '科技')}
"""

    def _format_article(self, report: str, topic: Dict) -> str:
        """拼接 frontmatter 与正文。"""
        now = datetime.now()
        slug = self._generate_slug(topic["title"])
        excerpt = self._extract_excerpt(report)
        tags = self._extract_tags(topic)

        frontmatter = (
            f"---\n"
            f"title: \"{topic['title']}\"\n"
            f"date: {now.strftime('%Y-%m-%d')}\n"
            f"time: {now.strftime('%H:%M:%S')}\n"
            f"slug: {slug}\n"
            f"source: {topic.get('source', '')}\n"
            f"source_url: {topic.get('url', '')}\n"
            f"engagement_score: {topic.get('engagement_score', 0)}\n"
            f"category: {topic.get('category', '科技')}\n"
            f"tags: {tags}\n"
            f"excerpt: \"{excerpt}\"\n"
            f"status: published\n"
            f"---"
        )

        return f"{frontmatter}\n\n{report}"

    def _generate_slug(self, title: str) -> str:
        """生成 URL 友好的 slug。"""
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug[:SLUG_MAX_LENGTH]

    def _extract_excerpt(self, content: str) -> str:
        """截取摘要，移除 Markdown 符号。"""
        plain = re.sub(r"[#*`\[\]()]", "", content)
        return plain[:EXCERPT_LENGTH].strip() + "..."

    def _extract_tags(self, topic: Dict) -> List[str]:
        """结合类别与关键词生成标签。"""
        tags: List[str] = []
        category = topic.get("category")
        if category:
            tags.append(category)

        title_lower = topic.get("title", "").lower()
        for keyword, tag in TAG_KEYWORDS.items():
            if keyword in title_lower:
                tags.append(tag)

        return tags[:5]
