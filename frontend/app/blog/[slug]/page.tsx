import { notFound } from 'next/navigation'
import Link from 'next/link'
import { Calendar, Clock, ExternalLink, Tag, TrendingUp, BookOpen, User, Share2, Bookmark } from 'lucide-react'
import { getAllSlugs, getArticleBySlug } from '@/lib/markdown'
import ReadingProgress from '@/components/ReadingProgress'
import TableOfContents from '@/components/TableOfContents'

export async function generateStaticParams() {
  const slugs = await getAllSlugs()
  return slugs.map((slug) => ({ slug }))
}

// 计算阅读时间
function calculateReadTime(content: string): number {
  const wordsPerMinute = 250
  const wordCount = content.split(/\s+/).length
  return Math.max(1, Math.ceil(wordCount / wordsPerMinute))
}

// 格式化日期
function formatDate(date: string): string {
  const d = new Date(date)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - d.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return '今天'
  if (diffDays === 1) return '昨天'
  if (diffDays < 7) return `${diffDays}天前`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)}月前`

  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export default async function ArticlePage({ params }: { params: { slug: string } }) {
  const article = await getArticleBySlug(params.slug)
  if (!article) {
    notFound()
    return null
  }

  const readTime = calculateReadTime(article.content)
  const formattedDate = formatDate(article.date)

  const sourceBadge: Record<string, string> = {
    hackernews: 'bg-gradient-to-r from-orange-400 to-amber-500',
    reddit: 'bg-gradient-to-r from-blue-500 to-indigo-600',
    github: 'bg-gradient-to-r from-slate-600 to-zinc-700',
    newsapi: 'bg-gradient-to-r from-emerald-500 to-teal-600',
  }

  return (
    <>
      <ReadingProgress />

      <div className="relative py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* 主内容区 */}
          <div className="lg:col-span-8">
            {/* 文章头部 */}
            <header className="rounded-3xl glass p-8 animate-fadeIn">
              {/* 面包屑导航 */}
              <nav className="mb-6 flex items-center gap-2 text-sm text-slate-500">
                <Link href="/" className="hover:text-teal-600 transition-colors">
                  <BookOpen size={16} className="inline mr-1" />
                  主页
                </Link>
                <span className="text-slate-400">/</span>
                <span className="text-slate-700 font-medium">{article.category || '深度研究'}</span>
              </nav>

              {/* 标题 */}
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-slate-900 leading-tight mb-6 gradient-text">
                {article.title}
              </h1>

              {/* 元信息 */}
              <div className="flex flex-wrap items-center gap-4 mb-6">
                <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium text-white shadow-lg ${
                  sourceBadge[article.source] || 'bg-gradient-to-r from-slate-400 to-gray-500'
                }`}>
                  {article.source.toUpperCase()}
                </span>

                <div className="flex items-center gap-4 text-sm text-slate-600">
                  <span className="flex items-center gap-1.5">
                    <Calendar size={16} />
                    {formattedDate}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Clock size={16} />
                    {readTime} 分钟阅读
                  </span>
                  {article.engagement_score && (
                    <span className="flex items-center gap-1.5">
                      <TrendingUp size={16} />
                      热度 {article.engagement_score}
                    </span>
                  )}
                </div>
              </div>

              {/* 标签 */}
              <div className="flex flex-wrap gap-2 mb-6">
                {article.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center gap-1 rounded-lg bg-gradient-to-r from-slate-100 to-zinc-100 px-3 py-1.5 text-xs font-medium text-slate-700 transition-all hover:from-teal-100 hover:to-blue-100"
                  >
                    <Tag size={12} />
                    {tag}
                  </span>
                ))}
              </div>

              {/* 摘要 */}
              <div className="rounded-2xl bg-gradient-to-r from-teal-50 to-blue-50 p-6">
                <p className="text-sm md:text-base leading-relaxed text-slate-700">
                  <strong className="text-teal-700">核心观点：</strong>
                  {article.excerpt}
                </p>
              </div>

              {/* 操作栏 */}
              <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-6">
                <div className="flex items-center gap-2">
                  <button className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm text-slate-600 transition-all hover:bg-slate-100">
                    <Share2 size={16} />
                    分享
                  </button>
                  <button className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm text-slate-600 transition-all hover:bg-slate-100">
                    <Bookmark size={16} />
                    收藏
                  </button>
                </div>

                {article.source_url && (
                  <a
                    href={article.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-teal-500 to-blue-600 px-4 py-2 text-sm font-medium text-white shadow-lg transition-all hover:shadow-xl"
                  >
                    <ExternalLink size={16} />
                    查看原文
                  </a>
                )}
              </div>
            </header>

            {/* 文章内容 */}
            <article className="mt-8 rounded-3xl glass p-8 animate-fadeIn">
              <div
                className="prose prose-lg prose-slate max-w-none
                  prose-headings:font-bold prose-headings:text-slate-900
                  prose-h2:text-2xl prose-h2:mt-10 prose-h2:mb-4 prose-h2:pb-2 prose-h2:border-b prose-h2:border-slate-200
                  prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-3
                  prose-p:text-slate-700 prose-p:leading-relaxed prose-p:mb-6
                  prose-a:text-teal-600 prose-a:no-underline hover:prose-a:text-blue-600
                  prose-strong:text-slate-900 prose-strong:font-bold
                  prose-code:text-rose-600 prose-code:bg-rose-50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:before:content-none prose-code:after:content-none
                  prose-pre:bg-slate-900 prose-pre:text-slate-100 prose-pre:rounded-xl prose-pre:shadow-lg
                  prose-blockquote:border-l-4 prose-blockquote:border-teal-500 prose-blockquote:bg-teal-50 prose-blockquote:py-4 prose-blockquote:px-6 prose-blockquote:rounded-r-xl prose-blockquote:italic
                  prose-ul:my-6 prose-ul:space-y-2
                  prose-ol:my-6 prose-ol:space-y-2
                  prose-li:text-slate-700
                  prose-img:rounded-xl prose-img:shadow-lg prose-img:my-8"
                dangerouslySetInnerHTML={{ __html: article.content }}
              />
            </article>

            {/* 文章底部 */}
            <footer className="mt-8 rounded-3xl glass p-8">
              <div className="flex items-center justify-between">
                <div className="text-sm text-slate-600">
                  <p>来源：{article.source}</p>
                  <p className="mt-1">字数：{article.wordCount?.toLocaleString() || '未知'}</p>
                </div>

                <Link
                  href="/"
                  className="rounded-lg bg-gradient-to-r from-teal-500 to-blue-600 px-6 py-3 text-sm font-medium text-white shadow-lg transition-all hover:shadow-xl"
                >
                  返回文章列表
                </Link>
              </div>
            </footer>
          </div>

          {/* 侧边栏 */}
          <aside className="lg:col-span-4">
            <TableOfContents />
          </aside>
        </div>
      </div>
    </>
  )
}
