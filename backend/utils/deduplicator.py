"""热点去重工具。"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Set

from backend.utils.config_loader import load_yaml_config

DEFAULT_THRESHOLD = 0.85
DEFAULT_CHECK_DAYS = 7
PROCESSED_DIR = Path("data/processed")


class Deduplicator:
    """根据标题相似度去重，并参考近几天已生成的记录。"""

    def __init__(self) -> None:
        config = load_yaml_config("backend/config/filter_rules.yaml")
        dedup_cfg = config.get("deduplication", {})
        self.similarity_threshold = dedup_cfg.get("similarity_threshold", DEFAULT_THRESHOLD)
        self.check_days = dedup_cfg.get("check_days", DEFAULT_CHECK_DAYS)
        self.history_titles = self._load_recent_titles()

    def deduplicate(self, items: List[Dict]) -> List[Dict]:
        """按相似度过滤重复标题。"""
        unique: List[Dict] = []

        for item in items:
            title = item.get("title", "")
            if not title:
                continue

            if self._is_duplicate(title, [u["title"] for u in unique]):
                continue
            if self._is_duplicate(title, self.history_titles):
                continue

            unique.append(item)

        return unique

    def _is_duplicate(self, title: str, corpus: List[str] | Set[str]) -> bool:
        """计算标题相似度，大于阈值视为重复。"""
        for existed in corpus:
            ratio = SequenceMatcher(None, title, existed).ratio()
            if ratio >= self.similarity_threshold:
                return True
        return False

    def _load_recent_titles(self) -> Set[str]:
        """读取最近若干天已处理的话题标题。"""
        titles: Set[str] = set()
        if not PROCESSED_DIR.exists():
            return titles

        today = datetime.now().date()
        for json_file in PROCESSED_DIR.glob("*.json"):
            try:
                date_part = json_file.stem
                file_date = datetime.fromisoformat(date_part).date()
            except ValueError:
                continue

            if (today - file_date).days > self.check_days:
                continue

            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue

            for item in data.get("items", []):
                title = item.get("title")
                if title:
                    titles.add(title)

        return titles
