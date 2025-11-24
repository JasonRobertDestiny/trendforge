"""热点筛选器。"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from backend.utils.config_loader import load_yaml_config

DEFAULT_RECENCY_HOURS = 24
DEFAULT_DAILY_LIMIT = 10
DEFAULT_WEIGHT = 1.0


class TrendingFilter:
    """按照热度、关键词与时效性筛选热点。"""

    def __init__(self) -> None:
        config = load_yaml_config("backend/config/filter_rules.yaml")
        self.engagement_thresholds = config.get("engagement_thresholds", {})
        self.platform_weights = config.get("platform_weights", {})
        self.recency_hours = config.get("recency_hours", DEFAULT_RECENCY_HOURS)
        self.daily_limit = config.get("daily_limit", DEFAULT_DAILY_LIMIT)
        self.keywords = self._collect_keywords(config.get("topic_keywords", {}))

    def filter_trending(self, items: List[Dict]) -> List[Dict]:
        """返回符合条件的热点（按热度降序，截断 daily_limit）。"""
        now = datetime.now()
        filtered: List[Dict] = []

        for item in items:
            if not item.get("title"):
                continue

            if not self._within_recency(item.get("published_at"), now):
                continue

            if not self._meet_engagement(item):
                continue

            if not self._contain_keyword(item["title"]):
                continue

            filtered.append(item)

        # 按权重后的热度排序
        filtered.sort(
            key=lambda x: self._weighted_score(x.get("source"), x.get("engagement_score", 0)),
            reverse=True,
        )
        return filtered[: self.daily_limit]

    def _within_recency(self, published_at, now: datetime) -> bool:
        """校验是否在时效窗口内。"""
        if not published_at:
            # 某些源不带时间戳，视为当前时间，避免误杀
            published_at = now
        if not isinstance(published_at, datetime):
            try:
                published_at = datetime.fromisoformat(str(published_at))
            except ValueError:
                return False
        return now - published_at <= timedelta(hours=self.recency_hours)

    def _meet_engagement(self, item: Dict) -> bool:
        """检查热度分数是否达标。"""
        source = item.get("source", "").lower()
        score = float(item.get("engagement_score", 0))
        threshold = self.engagement_thresholds.get(source, 0)
        return score >= threshold

    def _contain_keyword(self, title: str) -> bool:
        """标题需命中至少一个关键词。"""
        lower = title.lower()
        return any(kw in lower for kw in self.keywords)

    @staticmethod
    def _collect_keywords(keyword_group: Dict) -> List[str]:
        """扁平化关键词配置并转小写，便于快速匹配。"""
        all_kw: List[str] = []
        for group in keyword_group.values():
            all_kw.extend(group)
        return [kw.lower() for kw in all_kw]

    def _weighted_score(self, source: str, score: float) -> float:
        """应用平台权重后的排序分。"""
        weight = float(self.platform_weights.get(str(source).lower(), DEFAULT_WEIGHT))
        return float(score) * weight
