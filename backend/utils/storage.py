"""Git 存储工具。"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from git import Repo, GitCommandError

DEFAULT_TRACK_PATHS = ["content/", "data/"]


class GitStorage:
    """封装 Git 提交与推送操作。"""

    def __init__(self, repo_path: str = ".", track_paths: Iterable[str] | None = None) -> None:
        self.repo_path = Path(repo_path)
        self.track_paths: List[str] = list(track_paths or DEFAULT_TRACK_PATHS)
        self.repo = Repo(self.repo_path)

    def commit_and_push(self, message: str) -> None:
        """提交指定路径并尝试推送远程。"""
        try:
            self.repo.index.add(self.track_paths)
            if not self.repo.index.diff("HEAD"):
                print("   ⚠️  没有检测到需提交的变更，跳过提交")
                return

            self.repo.index.commit(message)
            print(f"   ✓ 已提交: {message}")

            if self.repo.remotes:
                origin = self.repo.remote("origin")
                origin.push()
                print("   ✓ 已推送到 origin")
            else:
                print("   ⚠️  未配置远程仓库，跳过推送")
        except GitCommandError as exc:
            print(f"   ⚠️  Git 操作失败: {exc}")
