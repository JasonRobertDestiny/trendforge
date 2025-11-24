"""简单的 YAML 配置加载器。"""
from __future__ import annotations

import yaml
from pathlib import Path
from typing import Dict


def load_yaml_config(path: str) -> Dict:
    """加载 YAML，若文件缺失返回空字典。"""
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp) or {}
