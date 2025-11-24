"""爬虫基类，约束输出格式并提供通用工具。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List


class BaseCrawler(ABC):
    """所有数据源爬虫需继承的抽象类。"""

    @abstractmethod
    async def fetch_trending(self) -> List[Dict]:
        """
        拉取热点列表。

        返回的每个元素应包含：
        - title: str
        - url: str
        - source: str
        - engagement_score: float
        - published_at: datetime
        - category: str
        - raw_data: 原始数据
        """

    @staticmethod
    def parse_datetime(value) -> datetime:
        """将时间戳或字符串转换为 datetime，失败时回退当前时间。"""
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return datetime.now()
        return datetime.now()
