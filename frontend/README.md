# TrendForge 前端（Next.js 14 静态站）

从 `/content/blog/*.md` 读取 DR 生成的文章，提供搜索、分类和详情浏览。

## 快速开始
```bash
cd frontend
npm install
npm run dev
```

构建静态站（输出到 `frontend/out`）：
```bash
npm run build
```

## 关键点
- App Router + TypeScript
- Tailwind + @tailwindcss/typography
- Markdown 解析：gray-matter + remark + rehype-highlight
- 默认从仓库根目录的 `content/blog` 读取文件，可与后端生成目录直接共享

## 页面
- `/` 首页：最新 12 篇 + 分类过滤
- `/blog/[slug]`：文章详情，含摘要、标签、原文链接
- `/search`：关键词/分类搜索，分页

## 环境变量
- `SITE_URL`（可选）在 `next.config.js` 使用
