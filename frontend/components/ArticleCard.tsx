import Link from 'next/link'
import { Calendar, Tag, TrendingUp, Clock, Eye } from 'lucide-react'
import { ArticleMetadata } from '@/lib/types'

interface Props {
  article: ArticleMetadata
}

const sourceTone: Record<string, string> = {
  hackernews: 'bg-gradient-to-r from-orange-400 to-amber-500 text-white',
  reddit: 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white',
  github: 'bg-gradient-to-r from-slate-600 to-zinc-700 text-white',
  newsapi: 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white',
}

// 计算阅读时间（基于中英文混合内容）
function calculateReadTime(wordCount: number): number {
  return Math.max(1, Math.ceil(wordCount / 250)) // 假设每分钟250字
}

export default function ArticleCard({ article }: Props) {
  const readTime = calculateReadTime(article.wordCount || 500)
  const hasHighEngagement = article.engagementScore && article.engagementScore > 100

  return (
    <article className="group relative flex h-full flex-col overflow-hidden rounded-2xl glass card-hover transition-all duration-300">
      {/* 热度标记 */}
      {hasHighEngagement && (
        <div className="absolute right-3 top-3 z-10">
          <div className="flex items-center gap-1 rounded-full bg-gradient-to-r from-red-500 to-orange-500 px-2 py-1 text-xs font-bold text-white shadow-lg">
            <TrendingUp size={12} />
            <span>热门</span>
          </div>
        </div>
      )}

      <Link href={`/blog/${article.slug}`} className="flex flex-1 flex-col p-5">
        {/* 顶部元信息 */}
        <div className="mb-3 flex items-center justify-between">
          <span className={`rounded-full px-3 py-1.5 text-xs font-medium shadow-md ${sourceTone[article.source] || 'bg-gradient-to-r from-slate-400 to-gray-500 text-white'}`}>
            {article.source.toUpperCase()}
          </span>
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Clock size={14} />
              {readTime} 分钟
            </span>
            <span className="flex items-center gap-1">
              <Calendar size={14} />
              {new Date(article.date).toLocaleDateString('zh-CN')}
            </span>
          </div>
        </div>

        {/* 标题 */}
        <h3 className="mb-3 text-lg font-bold leading-tight text-slate-900 transition-colors duration-200 group-hover:bg-gradient-to-r group-hover:from-teal-600 group-hover:to-blue-600 group-hover:bg-clip-text group-hover:text-transparent">
          {article.title}
        </h3>

        {/* 摘要 */}
        <p className="line-clamp-3 flex-1 text-sm leading-relaxed text-slate-600">
          {article.excerpt}
        </p>

        {/* 标签 */}
        <div className="mt-4 flex flex-wrap gap-2">
          {article.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 rounded-lg bg-gradient-to-r from-slate-100 to-zinc-100 px-2.5 py-1 text-xs font-medium text-slate-700 transition-all duration-200 hover:from-teal-100 hover:to-blue-100 hover:text-teal-700"
            >
              <Tag size={10} />
              {tag}
            </span>
          ))}
        </div>

        {/* 底部行动按钮 */}
        <div className="mt-5 flex items-center justify-between border-t border-slate-100 pt-4">
          <div className="flex items-center gap-3 text-xs text-slate-500">
            {article.engagementScore && (
              <span className="flex items-center gap-1">
                <Eye size={14} />
                {article.engagementScore}
              </span>
            )}
            {article.wordCount && (
              <span>{article.wordCount.toLocaleString()} 字</span>
            )}
          </div>
          <div className="flex items-center gap-1 text-sm font-semibold text-transparent bg-gradient-to-r from-teal-600 to-blue-600 bg-clip-text group-hover:gap-2 transition-all duration-200">
            <span>阅读全文</span>
            <span className="transition-transform duration-200 group-hover:translate-x-1">→</span>
          </div>
        </div>
      </Link>

      {/* 悬浮渐变边框效果 */}
      <div className="absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100">
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/20 via-blue-500/20 to-purple-500/20 blur-xl" />
        <div className="absolute inset-[1px] rounded-2xl bg-white/90" />
      </div>
    </article>
  )
}
