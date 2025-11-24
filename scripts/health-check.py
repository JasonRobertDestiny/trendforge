#!/usr/bin/env python3
"""TrendForge 运行健康检查脚本。"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BASE_DIR / "content" / "blog"
SITE_URL = os.getenv("SITE_URL", "https://trendforge.example.com")


def check_recent_content() -> Tuple[bool, str]:
    """检查当日是否生成内容。"""
    today = datetime.now().strftime("%Y-%m-%d")
    today_files = list(CONTENT_DIR.glob(f"*{today}*.md"))
    if not today_files:
        return False, "今日未生成内容"
    return True, f"今日生成 {len(today_files)} 篇"


def check_site() -> Tuple[bool, str]:
    """检查站点可访问性。"""
    try:
        resp = requests.get(SITE_URL, timeout=8)
        if resp.status_code == 200:
            return True, "站点正常"
        return False, f"站点返回 {resp.status_code}"
    except Exception as exc:  # noqa: BLE001
        return False, f"站点检查异常: {exc}"


def send_alert(message: str) -> None:
    """发送告警到 Webhook（可选）。"""
    webhook = os.getenv("ALERT_WEBHOOK")
    if not webhook:
        return
    try:
        requests.post(webhook, json={"text": message}, timeout=5)
    except Exception:
        pass


def main() -> None:
    checks = [
        ("内容生成", check_recent_content),
        ("站点可用性", check_site),
    ]

    ok = True
    report_lines = []

    for name, fn in checks:
        status, msg = fn()
        mark = "✓" if status else "✗"
        report_lines.append(f"{mark} {name}: {msg}")
        if not status:
            ok = False

    report = "\n".join(report_lines)
    if not ok:
        send_alert("⚠️ TrendForge 健康检查异常\n" + report)
        print(report)
        sys.exit(1)

    print(report)


if __name__ == "__main__":
    main()
